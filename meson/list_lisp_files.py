#!/usr/bin/env python3
"""Enumerate lisp/*.el files (excluding loaddefs) for byte-compilation.

Mirrors lisp/Makefile.in's $(setwins) logic, which finds every .el
file under lisp/ except those that should be skipped.  Produces a
newline-separated manifest of paths relative to lisp/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Files / patterns lisp/Makefile.in:357 skips during byte-compilation:
#   *loaddefs* -- generated files, not byte-compilable on their own.
#   COMPILE_FIRST list -- compiled separately first.  We do that
#                         via the compile-first target.
#   no-byte-compile cookie files -- header has ;;; ... -*- ... no-byte-compile: t.
SKIP_PATTERNS = ("loaddefs", "subdirs.el", "leim-list.el")


def is_no_byte_compile(p: Path) -> bool:
    try:
        with p.open(encoding="utf-8", errors="replace") as f:
            head = f.readline()
    except OSError:
        return False
    return "no-byte-compile: t" in head


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lisp-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    lisp = args.lisp_dir.resolve()
    out: list[str] = []
    for el in sorted(lisp.rglob("*.el")):
        rel = el.relative_to(lisp)
        if any(pat in rel.name for pat in SKIP_PATTERNS):
            continue
        if is_no_byte_compile(el):
            continue
        out.append(str(rel))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
