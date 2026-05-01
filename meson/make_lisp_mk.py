#!/usr/bin/env python3
"""Extract the shortlisp file list from lisp/loadup.el.

In the autotools build, src/Makefile.in:488 generates src/lisp.mk by
sed-extracting (load "FOO") forms from loadup.el and turning them into
a make variable assignment.  In the Meson build we don't need a
makefile fragment -- we just emit a JSON list that meson.build can
turn into a custom_target dependency.

This is a transitional helper used during the Meson migration; see
.claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# Match (load "name").  We replicate the sed pattern from
# src/Makefile.in:489: 's/^[ \t]*(load "\([^"]*\)".*/\1/p'.
_LOAD = re.compile(r'^\s*\(load\s+"([^"]+)"', re.MULTILINE)


def extract(loadup_path: Path) -> list[str]:
    text = loadup_path.read_text()
    out: list[str] = []
    for m in _LOAD.finditer(text):
        name = m.group(1)
        # Match the makefile rule's transformation:
        #   X         -> X.elc
        #   X.el      -> X.el (loaded as source)
        # i.e. files without an extension get .elc appended; files with
        # .el are loaded as source.  See src/Makefile.in:491.
        if name.endswith(".el"):
            out.append(name)
        else:
            out.append(name + ".elc")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path, help="path to lisp/loadup.el")
    p.add_argument("output", type=Path, help="path to write JSON to")
    args = p.parse_args()
    args.output.write_text(json.dumps(extract(args.input), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
