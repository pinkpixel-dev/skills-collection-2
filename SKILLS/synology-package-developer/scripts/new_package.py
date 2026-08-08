#!/usr/bin/env python3
"""Create a conservative DSM 7 package project from the bundled template."""

from __future__ import annotations

import argparse
import binascii
import re
import shutil
import struct
import sys
import zlib
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "package-template"
TOKEN_RE = re.compile(r"__[A-Z0-9_]+__")


def png_chunk(kind: bytes, data: bytes) -> bytes:
    payload = kind + data
    return struct.pack(">I", len(data)) + payload + struct.pack(
        ">I", binascii.crc32(payload) & 0xFFFFFFFF
    )


def make_png(path: Path, size: int, rgb: tuple[int, int, int]) -> None:
    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * size
    image = zlib.compress(row * size, level=9)
    path.write_bytes(
        signature
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", image)
        + png_chunk(b"IEND", b"")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_id", help="Stable DSM package identity")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--display-name")
    parser.add_argument("--description", default="A third-party package for Synology DSM.")
    parser.add_argument("--version", default="1.0.0-0001")
    parser.add_argument("--os-min-ver", default="7.2-64570")
    parser.add_argument("--toolkit-version", default="7.2.2")
    parser.add_argument("--arch", default="noarch")
    parser.add_argument("--maintainer", default="Package Maintainer")
    return parser.parse_args()


def validate(args: argparse.Namespace) -> None:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.package_id):
        raise ValueError("package_id must contain only letters, digits, dot, underscore, or hyphen")
    if any(char in args.package_id for char in ":/><|="):
        raise ValueError("package_id contains a DSM-forbidden character")
    if not re.fullmatch(r"\d+(?:[._-]\d+)+", args.version):
        raise ValueError("version must contain numeric segments separated by '.', '_' or '-'")
    if not re.fullmatch(r"\d+\.\d+-\d+", args.os_min_ver):
        raise ValueError("os_min_ver must look like 7.2-64570")
    if args.output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing path: {args.output_dir}")
    if not TEMPLATE.is_dir():
        raise FileNotFoundError(f"template not found: {TEMPLATE}")


def main() -> int:
    args = parse_args()
    created = False
    try:
        validate(args)
        display_name = args.display_name or args.package_id
        replacements = {
            "__PACKAGE_ID__": args.package_id,
            "__DISPLAY_NAME__": display_name,
            "__DESCRIPTION__": args.description,
            "__VERSION__": args.version,
            "__OS_MIN_VER__": args.os_min_ver,
            "__TOOLKIT_VERSION__": args.toolkit_version,
            "__ARCH__": args.arch,
            "__MAINTAINER__": args.maintainer,
        }

        shutil.copytree(TEMPLATE, args.output_dir)
        created = True
        for path in args.output_dir.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for token, value in replacements.items():
                text = text.replace(token, value)
            unresolved = TOKEN_RE.findall(text)
            if unresolved:
                raise ValueError(f"unresolved template tokens in {path}: {unresolved}")
            path.write_text(text, encoding="utf-8")

        make_png(args.output_dir / "PACKAGE_ICON.PNG", 64, (25, 100, 180))
        make_png(args.output_dir / "PACKAGE_ICON_256.PNG", 256, (25, 100, 180))

        executable_names = {
            "INFO.sh",
            "build",
            "install",
            "preinst",
            "postinst",
            "preuninst",
            "postuninst",
            "preupgrade",
            "postupgrade",
            "start-stop-status",
            "package-example",
        }
        args.output_dir.chmod(0o755)
        for path in args.output_dir.rglob("*"):
            if path.is_dir():
                path.chmod(0o755)
            elif path.is_file():
                path.chmod(0o755 if path.name in executable_names else 0o644)

        print(args.output_dir.resolve())
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        if created and args.output_dir.exists() and args.output_dir.is_dir():
            # Only remove the directory created by this invocation.
            shutil.rmtree(args.output_dir)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
