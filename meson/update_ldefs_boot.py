#!/usr/bin/env python3
"""Refresh lisp/ldefs-boot.el from the current generated loaddefs.el."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--stamp", required=True, type=Path)
    args = parser.parse_args()

    src_root = args.source_root.resolve()
    lisp_dir = src_root / "lisp"
    loaddefs = lisp_dir / "loaddefs.el"
    ldefs_boot = lisp_dir / "ldefs-boot.el"

    if not loaddefs.exists():
        print(f"missing generated file: {loaddefs}", file=sys.stderr)
        return 1

    if (not ldefs_boot.exists()
            or loaddefs.read_bytes() != ldefs_boot.read_bytes()):
        shutil.copy2(loaddefs, ldefs_boot)

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
