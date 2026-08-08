#!/usr/bin/env python3
"""Scaffold, validate, and reproducibly build minimal Audio Station .aum modules."""

from __future__ import annotations

import argparse
import io
import json
import re
import tarfile
from pathlib import Path


IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
MODULE_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


def validate_directory(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError("module root is not a directory")
    info_path = root / "INFO"
    try:
        manifest = json.loads(info_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("INFO is missing") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"INFO is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("INFO must contain a JSON object")
    required = {"name", "displayname", "version", "module", "type", "class"}
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError("INFO missing keys: " + ", ".join(missing))
    if not isinstance(manifest["name"], str) or not MODULE_NAME.fullmatch(manifest["name"]):
        raise ValueError("INFO name must be a conservative lowercase module identifier")
    if not isinstance(manifest["class"], str) or not IDENTIFIER.fullmatch(manifest["class"]):
        raise ValueError("INFO class must be a conservative PHP class identifier")
    module = manifest["module"]
    if not isinstance(module, str) or Path(module).name != module or not module.endswith(".php"):
        raise ValueError("INFO module must be a root-level .php basename")
    php_path = root / module
    try:
        php = php_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"configured PHP module is missing: {module}") from exc
    for needle in (f"class {manifest['class']}", "function getLyricsList", "function getLyrics",
                   "addTrackInfoToList", "addLyrics"):
        if needle not in php:
            raise ValueError(f"PHP module missing required construct: {needle}")
    forbidden = ("shell_exec(", "exec(", "system(", "passthru(", "unserialize(", "eval(")
    found = [item[:-1] for item in forbidden if item in php]
    if found:
        raise ValueError("PHP module contains high-risk calls: " + ", ".join(found))
    return manifest


def scaffold(root: Path, name: str, class_name: str, display_name: str) -> None:
    if root.exists():
        raise ValueError("output directory already exists")
    if not MODULE_NAME.fullmatch(name) or not IDENTIFIER.fullmatch(class_name):
        raise ValueError("invalid module name or class")
    root.mkdir(parents=True)
    manifest = {"name": name, "displayname": display_name, "description": "Configure provider description",
                "version": "0.1.0", "module": "lyric.php", "type": "lyric", "class": class_name}
    (root / "INFO").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    php = f'''<?php
class {class_name} {{
    public function getLyricsList($artist, $title, $info) {{
        // TODO: perform a bounded HTTPS provider lookup and validate its response.
        // $info->addTrackInfoToList($artist, $title, $id, $partialLyrics);
        return 0;
    }}

    public function getLyrics($id, $info) {{
        // TODO: validate $id, fetch from an allowlisted provider, and normalize text.
        // $info->addLyrics($lyric, $id);
        return false;
    }}
}}
?>
'''
    (root / "lyric.php").write_text(php, encoding="utf-8")


def build(root: Path, output: Path) -> None:
    manifest = validate_directory(root)
    if output.exists():
        raise ValueError("output archive already exists")
    members = ["INFO", manifest["module"]]
    with tarfile.open(output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for name in members:
            data = (root / name).read_bytes()
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime, info.uid, info.gid = len(data), 0o644, 0, 0, 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))


def validate_archive(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            if not member.isfile() or Path(member.name).name != member.name:
                raise ValueError(f"unsafe archive member: {member.name}")
        names = {member.name for member in members}
        if "INFO" not in names or not any(name.endswith(".php") for name in names):
            raise ValueError("archive must contain INFO and a root-level PHP module")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("scaffold")
    create.add_argument("root", type=Path)
    create.add_argument("--name", required=True)
    create.add_argument("--class-name", required=True)
    create.add_argument("--display-name", required=True)
    check = sub.add_parser("validate")
    check.add_argument("root", type=Path)
    package = sub.add_parser("build")
    package.add_argument("root", type=Path)
    package.add_argument("output", type=Path)
    archive = sub.add_parser("validate-archive")
    archive.add_argument("archive", type=Path)
    args = parser.parse_args()
    if args.command == "scaffold":
        scaffold(args.root, args.name, args.class_name, args.display_name)
    elif args.command == "validate":
        validate_directory(args.root)
    elif args.command == "build":
        build(args.root, args.output)
    else:
        validate_archive(args.archive)
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
