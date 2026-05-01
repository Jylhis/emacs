#!/usr/bin/env python3
"""Byte-compile a single .el file using bootstrap-emacs.

Wraps `bootstrap-emacs --batch --eval '(byte-compile-file ...)'` with
the env vars and load-path needed for an out-of-tree meson build.

See .claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# Subdirectories of lisp/ that the byte-compiler may need to find
# during compilation.  The autotools build relies on subdirs.el to
# auto-augment load-path; we simulate that by enumerating them.
LOAD_PATH_SUBDIRS = [
    "",
    "emacs-lisp",
    "international",
    "textmodes",
    "progmodes",
    "language",
    "vc",
    "calc",
    "calendar",
    "cedet",
    "cedet/ede",
    "cedet/semantic",
    "cedet/srecode",
    "emulation",
    "erc",
    "eshell",
    "gnus",
    "image",
    "mail",
    "mh-e",
    "mime",
    "net",
    "nxml",
    "obsolete",
    "org",
    "play",
    "term",
    "url",
]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp_root = src_root / "lisp"

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = ":".join(str(lisp_root / s) for s in LOAD_PATH_SUBDIRS)

    cmd = [
        args.bootstrap_emacs,
        "--batch",
        "--no-site-file",
        "--no-site-lisp",
        "--eval",
        f'(byte-compile-file "{args.input}")',
    ]
    rc = subprocess.run(cmd, env=env).returncode
    if rc != 0:
        return rc

    # byte-compile-file writes the .elc next to the source.  Move it.
    written = args.input.with_suffix(".elc")
    if not written.exists():
        print(f"byte-compile did not produce {written}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(written, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
