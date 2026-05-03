#!/usr/bin/env python3
"""Enumerate hicolor icon files matching the autotools install-etc rule.

Reproduces Makefile.in:802-820, which iterates `*/*/apps */*/mimetypes`
under `etc/images/icons/hicolor/` and installs every file matching the
shell glob `emacs[.-]*` (literal `emacs` + one `.` or `-` + suffix).
Files like `emacs22.png` and `emacs23.svg` do NOT match the glob.

Output: one line per file as TAB-separated `src_path<TAB>install_subdir`,
for the meson.build loop to consume via `run_command()`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path,
                   help="path to etc/images/icons/hicolor")
    p.add_argument("--icon-name", default="emacs",
                   help="basename to match (Makefile.in EMACS_ICON)")
    args = p.parse_args()

    if not args.root.is_dir():
        return 0

    # Mirror the shell glob: emacs followed by exactly one of '.' or '-',
    # then anything.  Use rsplit for robustness against mixed separators.
    def matches(name: str) -> bool:
        prefix = args.icon_name
        if not name.startswith(prefix):
            return False
        rest = name[len(prefix):]
        return bool(rest) and rest[0] in ".-"

    # iterate <size>/{apps,mimetypes} (depth-2 subdirs).
    for size_dir in sorted(args.root.iterdir()):
        if not size_dir.is_dir():
            continue
        for kind in ("apps", "mimetypes"):
            sub = size_dir / kind
            if not sub.is_dir():
                continue
            for f in sorted(sub.iterdir()):
                if f.is_file() and matches(f.name):
                    rel_subdir = f"{size_dir.name}/{kind}"
                    print(f"{f}\t{rel_subdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
