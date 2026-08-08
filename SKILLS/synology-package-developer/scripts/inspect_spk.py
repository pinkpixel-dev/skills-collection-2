#!/usr/bin/env python3
"""Read-only inspection of a tar-based Synology SPK and its package.tgz."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import stat
import sys
import tarfile
from pathlib import PurePosixPath, Path


SECRET_RE = re.compile(
    rb"(?i)(password|passwd|api[_-]?key|secret|token)\s*[=:]\s*['\"]?[^$\"'\s][^\"'\s]{3,}"
)


def unsafe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return path.is_absolute() or ".." in path.parts


def inspect_tar(tf: tarfile.TarFile, prefix: str = "") -> tuple[list[dict[str, object]], list[str]]:
    items: list[dict[str, object]] = []
    warnings: list[str] = []
    for member in tf.getmembers():
        label = f"{prefix}{member.name}"
        if unsafe_name(member.name):
            warnings.append(f"unsafe archive path: {label}")
        if member.issym() or member.islnk():
            if unsafe_name(member.linkname):
                warnings.append(f"unsafe link target: {label} -> {member.linkname}")
        if member.mode & stat.S_IWOTH:
            warnings.append(f"world-writable member: {label}")
        if member.mode & (stat.S_ISUID | stat.S_ISGID):
            warnings.append(f"setuid/setgid member: {label}")
        items.append(
            {
                "name": label,
                "size": member.size,
                "mode": f"{member.mode:04o}",
                "type": "dir" if member.isdir() else "file" if member.isfile() else "link" if member.issym() else "other",
            }
        )
        if member.isfile() and member.size <= 2_000_000:
            stream = tf.extractfile(member)
            data = stream.read() if stream else b""
            if SECRET_RE.search(data):
                warnings.append(f"possible embedded secret: {label}")
    return items, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spk", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = args.spk.resolve()
    if not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        return 2

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    report: dict[str, object] = {"path": str(path), "sha256": digest, "members": [], "warnings": []}
    try:
        with tarfile.open(path, "r:*") as tf:
            items, warnings = inspect_tar(tf)
            report["members"] = items
            report["warnings"] = warnings
            names = {member.name.lstrip("./"): member for member in tf.getmembers()}
            required = {"INFO", "package.tgz", "scripts", "conf", "PACKAGE_ICON.PNG", "PACKAGE_ICON_256.PNG"}
            top = {name.split("/", 1)[0] for name in names}
            for missing in sorted(required - top):
                warnings.append(f"missing top-level member: {missing}")
            payload_member = names.get("package.tgz")
            if payload_member and payload_member.isfile():
                payload_stream = tf.extractfile(payload_member)
                payload_data = payload_stream.read() if payload_stream else b""
                with tarfile.open(fileobj=io.BytesIO(payload_data), mode="r:*") as payload:
                    payload_items, payload_warnings = inspect_tar(payload, "package.tgz:")
                    report["payload_members"] = payload_items
                    warnings.extend(payload_warnings)
    except (tarfile.TarError, OSError) as exc:
        print(f"error: cannot inspect SPK as tar archive: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"SPK: {path}")
        print(f"SHA-256: {digest}")
        print(f"Top-level members: {len(report['members'])}")
        print(f"Payload members: {len(report.get('payload_members', []))}")
        warnings = report["warnings"]
        for warning in warnings:
            print(f"WARN: {warning}")
        print(f"Summary: {len(warnings)} warning(s)")
    return 1 if report["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
