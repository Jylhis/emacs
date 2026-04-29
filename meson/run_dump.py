#!/usr/bin/env python3
"""Run bootstrap-emacs to produce bootstrap-emacs.pdmp (or emacs.pdmp).

This wraps the autotools src/Makefile.in:870-895 dump cycle in a way
meson can drive via custom_target.  It chdirs to the source tree's
src/ directory so ../lisp resolves correctly, sets EMACSDATA so the
charset maps in etc/ are found, and copies the lisp/international/
generated files into place if they were produced in the build tree.

See .claude/plans/migrate-from-current-build-replicated-gadget.md.
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
    p.add_argument("--bootstrap-emacs", required=True,
                   help="path to bootstrap-emacs binary")
    p.add_argument("--source-root", required=True, type=Path,
                   help="path to Emacs source root")
    p.add_argument("--output-pdmp", required=True, type=Path,
                   help="path the dump should land at")
    p.add_argument("--mode", default="pbootstrap",
                   choices=["pbootstrap", "pdump"])
    p.add_argument("--charscript", type=Path,
                   help="generated lisp/international/charscript.el")
    p.add_argument("--emoji-zwj", type=Path,
                   help="generated lisp/international/emoji-zwj.el")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    src_dir = src_root / "src"

    # Stage the unidata-generated files into lisp/international/ if
    # they aren't already there.  Symlink so subsequent builds see
    # updates.
    lisp_intl = src_root / "lisp/international"
    for staged, fname in [
        (args.charscript, "charscript.el"),
        (args.emoji_zwj, "emoji-zwj.el"),
    ]:
        if staged is None:
            continue
        target = lisp_intl / fname
        if not target.exists() or target.read_bytes() != staged.read_bytes():
            shutil.copy(staged, target)

    # For --temacs=pbootstrap, loadup.el reads .el sources rather than
    # generated loaddefs.el (which won't exist yet); but if a stale
    # loaddefs.el is left in lisp/ from a prior build it can shadow
    # ldefs-boot.el and inject autoloads that aren't valid during
    # early bootstrap (e.g. frameset-filter-alist before
    # frameset.el is loaded).  See lisp/loadup.el:174.
    if args.mode == "pbootstrap":
        for stale in [src_root / "lisp/loaddefs.el"]:
            if stale.exists():
                stale.unlink()

    # Run bootstrap-emacs from src/ so PATH_DUMPLOADSEARCH ("../lisp")
    # resolves to the source tree's lisp/.
    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = str(src_root / "lisp")

    out_dir = args.output_pdmp.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        args.bootstrap_emacs,
        "--batch", "-l", "loadup",
        f"--temacs={args.mode}",
        "--bin-dest", str(out_dir / "bin"),
        "--eln-dest", str(out_dir / "native-lisp"),
    ]
    print("running:", " ".join(cmd), "(cwd:", src_dir, ")", flush=True)
    rc = subprocess.run(cmd, cwd=src_dir, env=env).returncode
    if rc != 0:
        return rc

    # bootstrap-emacs writes the pdmp next to its own binary, not to
    # CWD.  Move it to the requested output path.
    fname = ("bootstrap-emacs.pdmp" if args.mode == "pbootstrap"
             else "emacs.pdmp")
    candidates = [
        Path(args.bootstrap_emacs).parent / fname,
        src_dir / fname,
    ]
    for written in candidates:
        if written.exists():
            shutil.move(written, args.output_pdmp)
            return 0
    print(f"bootstrap-emacs did not produce {fname} in any of {candidates}",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
