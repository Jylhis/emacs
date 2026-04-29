#!/usr/bin/env python3
"""Emit buildobj.h: each src/ object filename as a C string literal.

Mirrors the for/sed loop in src/Makefile.in:591.  Used by doc.c to
attribute primitives to their source files.
"""

import sys
from pathlib import Path


def main() -> int:
    out_path = Path(sys.argv[1])
    names = sys.argv[2:]
    body = "".join(
        '"' + n.replace(".c", ".o").replace(".m", ".o") + '",\n'
        for n in names
    )
    out_path.write_text(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
