#!/usr/bin/env python3
"""Convert an .org file to .texi via emacs -l ox-texinfo.

Mirrors the org_template rule in doc/misc/Makefile.in at anchor
08a22b8965ec:

    cd $srcdir && emacs -l ox-texinfo \\
      --eval '(setq gc-cons-threshold 50000000)' \\
      --eval '(setq org-confirm-babel-evaluate nil)' \\
      --eval '(setq org-id-track-globally nil)' \\
      -f org-texinfo-export-to-texinfo-batch foo.org foo.texi

The dumped Emacs (built emacs.pdmp + emacs binary) is required;
bootstrap-emacs lacks the ox-texinfo dependencies.

The conversion is run inside doc/misc/ so the org-setup.org
@include (e.g. org-setup.org) resolves; the produced .texi file
is moved to the requested build-tree output path.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emacs", required=True, type=Path,
                   help="path to the built emacs binary")
    p.add_argument("--dump-file", required=True, type=Path,
                   help="path to emacs.pdmp")
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--input", required=True, type=Path,
                   help="path to .org file (under doc/misc/)")
    p.add_argument("--output", required=True, type=Path,
                   help="destination .texi path (build tree)")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    misc_dir = (src_root / "doc/misc").resolve()
    org_path = args.input.resolve()
    out_path = args.output.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ox-texinfo's batch entry point writes the output next to the
    # input by default and accepts a positional output path.  It is
    # robust against absolute paths.
    env = os.environ.copy()
    lisp = src_root / "lisp"
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    # Enumerate every direct subdir of lisp/ so ox-texinfo (which
    # lives at lisp/org/ox-texinfo.el) is on the load path.  Mirrors
    # the EMACSLOADPATH composition in meson/run_loaddefs.py.
    paths = [str(lisp)] + sorted(
        str(p) for p in lisp.iterdir() if p.is_dir()
    )
    env["EMACSLOADPATH"] = ":".join(paths)

    # Emit the .texi alongside the .org temporarily, then move it.
    # This matches the autotools rule's `cd $srcdir && ...` semantics
    # and keeps any relative @includes resolvable.
    tmp_texi = misc_dir / (org_path.stem + ".texi")
    cmd = [
        str(args.emacs),
        f"--dump-file={args.dump_file}",
        "--batch", "-Q",
        "-l", "ox-texinfo",
        "--eval", "(setq gc-cons-threshold 50000000)",
        "--eval", "(setq org-confirm-babel-evaluate nil)",
        "--eval", "(setq org-id-track-globally nil)",
        "-f", "org-texinfo-export-to-texinfo-batch",
        org_path.name, tmp_texi.name,
    ]
    print("running:", " ".join(cmd), "(cwd:", misc_dir, ")", flush=True)
    rc = subprocess.run(cmd, cwd=misc_dir, env=env).returncode
    if rc != 0:
        return rc

    if not tmp_texi.exists():
        print(f"ox-texinfo did not produce {tmp_texi}", file=sys.stderr)
        return 1
    shutil.move(tmp_texi, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
