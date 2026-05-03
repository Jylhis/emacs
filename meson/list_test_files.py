#!/usr/bin/env python3
"""Enumerate test/**/*-tests.el for `meson test` discovery."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--test-dir", required=True, type=Path)
    p.add_argument("--output", required=True,
                   help='destination path, or "-" for stdout')
    args = p.parse_args()

    test = args.test_dir.resolve()
    out: list[str] = []
    for el in sorted(test.rglob("*-tests.el")):
        rel = el.relative_to(test)
        out.append(str(rel))

    payload = "\n".join(out) + "\n"
    if args.output == "-":
        sys.stdout.write(payload)
    else:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
