#!/usr/bin/env python3
"""Enumerate test/**/*-tests.el for `meson test` discovery."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--test-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    test = args.test_dir.resolve()
    out: list[str] = []
    for el in sorted(test.rglob("*-tests.el")):
        rel = el.relative_to(test)
        out.append(str(rel))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
