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
#   subdirs.el / leim-list.el -- generated path-tabulators.
#   no-byte-compile cookie files -- header has ;;; ... -*- ... no-byte-compile: t.
#
# loaddefs.el and *-loaddefs.el files ARE byte-compiled by autotools
# (the SUBDIRS glob picks them up).  Without loaddefs.elc the eager
# macro expander hits autoloaded macros at load time and pdump
# refuses to autoload during dump.  See lisp/loaddefs.el's defmacro
# tramp-archive-autoload-file-name-regexp for an example.
SKIP_PATTERNS = ("subdirs.el", "leim-list.el")


def is_no_byte_compile(p: Path) -> bool:
    # Emacs honours a `no-byte-compile: t' file-local variable in either
    # the first-line `-*- ... -*-' cookie or a `Local Variables:' block
    # near the end of the file; batch-byte-compile then silently refuses
    # to compile the file.  Inspecting only the first line (as before)
    # missed generated data files that carry the cookie in a trailing
    # Local Variables block -- international/uni-*.el, charprop.el,
    # ldefs-boot.el, loadup.el, theme-loaddefs.el, org/org-version.el --
    # which then entered the manifest and were miscounted as compile
    # errors.  Check both ends.  Work in bytes to avoid decoding the
    # multi-megabyte loaddefs.el / ldefs-boot.el in full; Emacs itself
    # only scans the last few KB for the Local Variables block.
    needle = b"no-byte-compile: t"
    try:
        data = p.read_bytes()
    except OSError:
        return False
    if needle in data[:256]:        # first-line -*- ... -*- cookie
        return True
    return needle in data[-3000:]   # trailing Local Variables block


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lisp-dir", required=True, type=Path)
    p.add_argument("--output", required=True,
                   help='destination path, or "-" for stdout')
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
