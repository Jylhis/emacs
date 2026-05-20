#!/usr/bin/env python3
"""Run bootstrap-emacs to produce bootstrap-emacs.pdmp (or emacs.pdmp).

This wraps the autotools src/Makefile.in:870-895 dump cycle in a way
meson can drive via custom_target.  It chdirs to the source tree's
src/ directory so ../lisp resolves correctly, sets EMACSDATA so the
charset maps in etc/ are found, and copies the lisp/international/
generated files into place if they were produced in the build tree.
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
    p.add_argument("--doc-file", type=Path,
                   help="generated etc/DOC; required for pdump mode "
                        "where loadup.el's Snarf-documentation reads it.")
    p.add_argument("--no-build-details", action="store_true",
                   help="pass --no-build-details to the dump invocation "
                        "(omits build time, host name, etc. from the "
                        "dumped image; mirrors autotools BUILD_DETAILS).")
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

    # Stage etc/DOC -- loadup.el's (Snarf-documentation "DOC") looks
    # for it under EMACSDOC = src_root/etc/.
    if args.doc_file is not None and args.doc_file.exists():
        etc_doc = src_root / "etc/DOC"
        etc_doc.parent.mkdir(parents=True, exist_ok=True)
        if (not etc_doc.exists()
                or etc_doc.read_bytes() != args.doc_file.read_bytes()):
            shutil.copy(args.doc_file, etc_doc)

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

    # For pdump mode, loadup.el expects to find byte-compiled .elc
    # files.  Meson puts them in build/lisp/, but the source tree
    # lisp/ has only .el.  Stage the .elc files alongside their
    # sources so load() picks them up via PATH_DUMPLOADSEARCH.  The
    # source tree's .el remains canonical; only .elc is added.
    if args.mode == "pdump":
        # Locate build/lisp by walking up from output-pdmp.  The
        # output is build/src/emacs.pdmp; build/lisp is a sibling.
        build_lisp = args.output_pdmp.parent.parent / "lisp"
        if build_lisp.is_dir():
            for elc in build_lisp.rglob("*.elc"):
                rel = elc.relative_to(build_lisp)
                target = src_root / "lisp" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if (not target.exists()
                        or target.stat().st_mtime < elc.stat().st_mtime):
                    shutil.copy2(elc, target)

    out_dir = args.output_pdmp.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [args.bootstrap_emacs, "--batch"]
    if args.no_build_details:
        cmd.append("--no-build-details")
    cmd += [
        "-l", "loadup",
        f"--temacs={args.mode}",
        "--bin-dest", str(out_dir / "bin"),
        "--eln-dest", str(out_dir / "native-lisp"),
    ]
    print("running:", " ".join(cmd), "(cwd:", src_dir, ")", flush=True)
    result = subprocess.run(cmd, cwd=src_dir, env=env,
                            capture_output=True, text=True)
    if result.stdout:
        sys.stdout.write(result.stdout)
        sys.stdout.flush()
    if result.returncode != 0:
        rc = result.returncode
        print(f"bootstrap-emacs exited with code {rc}", file=sys.stderr)
        if rc < 0:
            import signal as _sig
            try:
                name = _sig.Signals(-rc).name
            except (ValueError, AttributeError):
                name = f"signal {-rc}"
            print(f"  (killed by {name})", file=sys.stderr)
        if result.stderr:
            sys.stderr.write(result.stderr)
            sys.stderr.flush()
        return abs(rc) if rc > 0 else 128 + (-rc)


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
