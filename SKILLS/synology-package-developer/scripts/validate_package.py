#!/usr/bin/env python3
"""Offline static validator for a DSM package source or staged SPK directory."""

from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from pathlib import Path


REQUIRED_INFO = {"package", "version", "os_min_ver", "description", "arch", "maintainer"}
REQUIRED_SCRIPTS = {
    "preinst",
    "postinst",
    "preuninst",
    "postuninst",
    "preupgrade",
    "postupgrade",
    "start-stop-status",
}
FORBIDDEN_INFO_DSM7 = {"startable"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|api[_-]?key|secret|token)\s*[=:]\s*['\"]?[^$\"'\s][^\"'\s]{3,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
DANGEROUS_SHELL = [
    (re.compile(r"\brm\s+-[^\n]*r[^\n]*\s+/(?:\s|$)"), "recursive deletion targeting /"),
    (re.compile(r"\brm\s+-[^\n]*r[^\n]*\s+/(?:volume1|volume2)(?:\s|/|$)"), "broad volume deletion"),
    (re.compile(r"\bchmod\s+-R\b"), "recursive chmod"),
    (re.compile(r"\bchown\s+-R\b"), "recursive chown"),
    (re.compile(r"\beval\b"), "eval usage"),
    (re.compile(r"curl[^|\n]*\|\s*(?:sh|bash)\b"), "remote script piped to shell"),
    (re.compile(r"wget[^|\n]*\|\s*(?:sh|bash)\b"), "remote script piped to shell"),
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--target-dsm", default="7.2.2")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    return parser.parse_args()


def read_text(path: Path, report: Report) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report.error(f"{path}: cannot read UTF-8 text: {exc}")
        return ""


def parse_info_text(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(['\"]?)(.*?)\2\s*$")
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = pattern.match(line)
        if match:
            result[match.group(1)] = match.group(3)
    return result


def locate(project: Path, *candidates: str) -> Path | None:
    for candidate in candidates:
        path = project / candidate
        if path.exists():
            return path
    return None


def check_info(project: Path, report: Report, dsm_major: int) -> None:
    info_path = locate(project, "INFO", "INFO.sh")
    if info_path is None:
        report.error("missing INFO or INFO.sh")
        return
    text = read_text(info_path, report)
    fields = parse_info_text(text)
    missing = sorted(REQUIRED_INFO - fields.keys())
    if missing:
        report.error(f"{info_path}: missing required fields: {', '.join(missing)}")

    package = fields.get("package", "")
    if package and (re.search(r"[:/><|=]", package) or not re.fullmatch(r"[A-Za-z0-9._-]+", package)):
        report.error(f"{info_path}: invalid package identity {package!r}")

    version = fields.get("version", "")
    if version and not re.fullmatch(r"\d+(?:[._-]\d+)+", version):
        report.error(f"{info_path}: version should contain numeric segments only")

    os_min = fields.get("os_min_ver", "")
    match = re.fullmatch(r"(\d+)\.(\d+)-(\d+)", os_min)
    if os_min and not match:
        report.error(f"{info_path}: malformed os_min_ver {os_min!r}")
    elif match and dsm_major >= 7 and (int(match.group(1)), int(match.group(3))) < (7, 40000):
        report.error(f"{info_path}: DSM 7 package os_min_ver must be at least 7.0-40000")

    if dsm_major >= 7:
        deprecated = sorted(FORBIDDEN_INFO_DSM7 & fields.keys())
        if deprecated:
            report.warn(f"{info_path}: deprecated DSM 7 fields: {', '.join(deprecated)}")

    if fields.get("arch") == "noarch":
        native = list(project.rglob("*.so")) + list(project.rglob("*.a"))
        if native:
            report.warn(f"{info_path}: arch=noarch but native-library-looking files exist")

    for regex in SECRET_PATTERNS:
        if regex.search(text):
            report.error(f"{info_path}: possible embedded secret")


def check_json(path: Path, report: Report) -> object | None:
    if not path.exists():
        report.error(f"missing {path}")
        return None
    try:
        return json.loads(read_text(path, report))
    except json.JSONDecodeError as exc:
        report.error(f"{path}: invalid JSON: {exc}")
        return None


def check_privilege(project: Path, report: Report, dsm_major: int) -> None:
    privilege = locate(project, "conf/privilege", "package/conf/privilege")
    if privilege is None:
        if dsm_major >= 7:
            report.error("missing conf/privilege for DSM 7")
        return
    data = check_json(privilege, report)
    if not isinstance(data, dict):
        return
    defaults = data.get("defaults")
    if not isinstance(defaults, dict):
        report.error(f"{privilege}: missing defaults object")
        return
    run_as = defaults.get("run-as")
    if dsm_major >= 7 and run_as != "package":
        report.error(f"{privilege}: DSM 7 should use defaults.run-as=package")
    for section in ("tool", "executable"):
        entries = data.get(section, [])
        if not isinstance(entries, list):
            report.error(f"{privilege}: {section} must be an array")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                report.error(f"{privilege}: {section}[{index}] must be an object")
                continue
            relpath = entry.get("relpath", "")
            if relpath.startswith("/") or ".." in Path(relpath).parts:
                report.error(f"{privilege}: unsafe relpath in {section}[{index}]")
            permission = str(entry.get("permission", ""))
            if permission and not re.fullmatch(r"[0-7]{4}", permission):
                report.error(f"{privilege}: invalid permission {permission!r}")
            if permission and int(permission, 8) & (stat.S_ISUID | stat.S_ISGID | stat.S_IWOTH):
                report.warn(f"{privilege}: high-risk mode {permission} in {section}[{index}]")


def check_resource(project: Path, report: Report) -> None:
    resource = locate(project, "conf/resource", "package/conf/resource")
    if resource is None:
        report.warn("missing conf/resource; valid only when no resource workers are needed")
        return
    data = check_json(resource, report)
    if not isinstance(data, dict):
        return
    serialized = json.dumps(data)
    for regex in SECRET_PATTERNS:
        if regex.search(serialized):
            report.error(f"{resource}: possible embedded secret")
    if "docker" in data:
        report.warn(f"{resource}: legacy docker worker present; consider docker-project on DSM 7.2.1+")


def check_scripts(project: Path, report: Report) -> None:
    scripts_dir = locate(project, "scripts", "package/scripts")
    if scripts_dir is None or not scripts_dir.is_dir():
        report.error("missing scripts directory")
        return
    missing = sorted(name for name in REQUIRED_SCRIPTS if not (scripts_dir / name).is_file())
    if missing:
        report.error(f"{scripts_dir}: missing lifecycle scripts: {', '.join(missing)}")
    for path in scripts_dir.iterdir():
        if not path.is_file():
            continue
        text = read_text(path, report)
        if not text.startswith("#!"):
            report.warn(f"{path}: missing shebang")
        if not path.stat().st_mode & stat.S_IXUSR:
            report.warn(f"{path}: not owner-executable")
        for regex, label in DANGEROUS_SHELL:
            if regex.search(text):
                report.warn(f"{path}: {label}")
        for regex in SECRET_PATTERNS:
            if regex.search(text):
                report.error(f"{path}: possible embedded secret")
    status = scripts_dir / "start-stop-status"
    if status.exists() and "status)" not in read_text(status, report):
        report.error(f"{status}: missing status action")


def check_build(project: Path, report: Report) -> None:
    build_dir = project / "SynoBuildConf"
    if not build_dir.exists():
        report.warn("missing SynoBuildConf; staged SPK directories may omit it")
        return
    for name in ("depends", "build", "install"):
        path = build_dir / name
        if not path.is_file():
            report.error(f"missing {path}")
    for name in ("build", "install"):
        path = build_dir / name
        if path.exists() and not path.stat().st_mode & stat.S_IXUSR:
            report.warn(f"{path}: not owner-executable")


def check_icons(project: Path, report: Report, dsm_major: int) -> None:
    expected = {"PACKAGE_ICON.PNG": 64 if dsm_major >= 7 else 72, "PACKAGE_ICON_256.PNG": 256}
    for name, size in expected.items():
        path = project / name
        if not path.exists():
            report.error(f"missing {path}")
            continue
        data = path.read_bytes()
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            report.error(f"{path}: not a PNG")
            continue
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        if (width, height) != (size, size):
            report.error(f"{path}: expected {size}x{size}, got {width}x{height}")


def check_tree(project: Path, report: Report) -> None:
    for path in project.rglob("*"):
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            report.error(f"{path}: stat failed: {exc}")
            continue
        if stat.S_ISLNK(mode):
            target = path.readlink()
            if target.is_absolute() or ".." in target.parts:
                report.warn(f"{path}: symlink escapes or uses parent traversal: {target}")
        if stat.S_ISREG(mode):
            if mode & stat.S_IWOTH:
                report.warn(f"{path}: world-writable")
            if mode & (stat.S_ISUID | stat.S_ISGID):
                report.warn(f"{path}: setuid/setgid bit present")


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    report = Report()
    if not project.is_dir():
        print(f"error: not a directory: {project}", file=sys.stderr)
        return 2
    try:
        dsm_major = int(args.target_dsm.split(".", 1)[0])
    except ValueError:
        print("error: --target-dsm must begin with a numeric major version", file=sys.stderr)
        return 2

    check_info(project, report, dsm_major)
    check_privilege(project, report, dsm_major)
    check_resource(project, report)
    check_scripts(project, report)
    check_build(project, report)
    check_icons(project, report, dsm_major)
    check_tree(project, report)

    for item in report.errors:
        print(f"ERROR: {item}")
    for item in report.warnings:
        print(f"WARN: {item}")
    print(f"Summary: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
