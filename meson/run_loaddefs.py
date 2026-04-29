#!/usr/bin/env python3
"""Generate loaddefs.el and *-loaddefs.el for the lisp/ tree.

Wraps `bootstrap-emacs -l loaddefs-gen.el -f loaddefs-generate--emacs-batch`
which is what lisp/Makefile.in:202 invokes.  The generated files land
in the source tree (lisp/loaddefs.el, lisp/emacs-lisp/cl-loaddefs.el,
lisp/theme-loaddefs.el, etc.); we touch a stamp file so meson can
track success.

See .claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--stamp", required=True, type=Path)
    p.add_argument("--subdirs", nargs="+", required=True,
                   help="lisp/ subdirectories to scan (e.g. emacs-lisp net mail)")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp = src_root / "lisp"

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = str(lisp)

    cmd = [
        args.bootstrap_emacs,
        "--batch", "--no-site-file", "--no-site-lisp",
        "-l", str(lisp / "emacs-lisp/loaddefs-gen.el"),
        "-f", "loaddefs-generate--emacs-batch",
    ] + [str(lisp / d) for d in args.subdirs]

    rc = subprocess.run(cmd, env=env).returncode
    if rc != 0:
        return rc

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
