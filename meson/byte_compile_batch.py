#!/usr/bin/env python3
"""Byte-compile a batch of .el files using bootstrap-emacs.

Wraps `bootstrap-emacs --batch -f batch-byte-compile FILE...` (the
mode lisp/Makefile.in:329 uses) and moves the produced .elc files
into a separate output tree so the source tree stays clean for
out-of-tree meson builds.

See .claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# Build EMACSLOADPATH from lisp/ recursively.  emacs-lisp must come
# first so the core 'debug feature resolves to lisp/emacs-lisp/debug,
# not lisp/cedet/semantic/debug.
def _load_path(lisp_root: Path) -> list[str]:
    paths = [str(lisp_root)]
    paths.append(str(lisp_root / "emacs-lisp"))
    skip = {"emacs-lisp", "obsolete"}
    for d in sorted(lisp_root.rglob("*")):
        if not d.is_dir():
            continue
        rel = d.relative_to(lisp_root).as_posix()
        if rel in skip or any(rel.startswith(s + "/") for s in skip):
            continue
        paths.append(str(d))
    return paths


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path,
                   help="root of the build/lisp tree")
    p.add_argument("--lisp-dir", required=True, type=Path,
                   help="root of the source/lisp tree")
    p.add_argument("--manifest", required=True, type=Path,
                   help="newline-separated list of .el files relative to lisp-dir")
    p.add_argument("--stamp", type=Path,
                   help="touch this file when the batch succeeds")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp_root = args.lisp_dir.resolve()

    rel_files = [Path(line.strip())
                 for line in args.manifest.read_text().splitlines()
                 if line.strip()]
    abs_files = [str(lisp_root / r) for r in rel_files]

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = ":".join(_load_path(lisp_root))
    # Match the BYTE_COMPILE_FLAGS in lisp/Makefile.in:78.
    env["BYTE_COMPILE_DEBUG"] = "1"

    cmd = [
        args.bootstrap_emacs,
        "--batch",
        "--no-site-file",
        "--no-site-lisp",
        "--eval",
        "(setq load-prefer-newer t byte-compile-warnings 'all)",
        "--eval",
        "(setq org--inhibit-version-check t)",
        "-f", "batch-byte-compile",
    ] + abs_files
    rc = subprocess.run(cmd, env=env).returncode
    if rc != 0:
        return rc

    # batch-byte-compile writes the .elc next to each .el.  Move them
    # into the build tree, preserving the relative layout.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for rel in rel_files:
        elc_src = lisp_root / rel.with_suffix(".elc")
        elc_dst = args.output_dir / rel.with_suffix(".elc")
        if not elc_src.exists():
            print(f"missing {elc_src}", file=sys.stderr)
            return 1
        elc_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(elc_src, elc_dst)
    if args.stamp is not None:
        args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
