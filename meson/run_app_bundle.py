#!/usr/bin/env python3
"""Assemble nextstep/Emacs.app from the Cocoa skeleton + emacs binary.

Mirrors the autotools rule in nextstep/Makefile.in at anchor
08a22b8965ec: copy the Cocoa skeleton, drop the rendered Info.plist,
and place the freshly built emacs binary at
Contents/MacOS/Emacs.

Optional --self-contained mode also copies lisp/, etc/, info/, and
the emacs.pdmp into Contents/Resources/ so the bundle can run
without the share/emacs install tree.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def copytree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        out = dst / rel
        out.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(Path(root) / f, out / f)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skeleton", required=True, type=Path,
                   help="path to nextstep/Cocoa/Emacs.base")
    p.add_argument("--bundle", required=True, type=Path,
                   help="output Emacs.app directory")
    p.add_argument("--info-plist", required=True, type=Path,
                   help="rendered Info.plist for Contents/Info.plist")
    p.add_argument("--emacs-binary", required=True, type=Path,
                   help="path to the built emacs binary")
    p.add_argument("--stamp", required=True, type=Path)
    p.add_argument("--self-contained", action="store_true",
                   help="copy lisp/, etc/, info/, emacs.pdmp into "
                        "Contents/Resources/")
    p.add_argument("--lisp-dir", type=Path,
                   help="(self-contained) path to source lisp/ tree")
    p.add_argument("--etc-dir", type=Path,
                   help="(self-contained) path to source etc/ tree")
    p.add_argument("--info-dir", type=Path,
                   help="(self-contained) path to build/doc/ holding "
                        "*.info to bundle")
    p.add_argument("--pdmp", type=Path,
                   help="(self-contained) path to emacs.pdmp")
    args = p.parse_args()

    bundle = args.bundle if args.bundle.is_absolute() else Path.cwd() / args.bundle
    if bundle.is_symlink():
        p.error(f"refusing to operate on symlinked bundle path: {bundle}")
    if bundle.exists():
        if not bundle.is_dir():
            p.error(f"bundle path exists and is not a directory: {bundle}")
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)

    # Copy the Cocoa skeleton.
    copytree(args.skeleton, bundle)

    # Drop Info.plist into Contents/.
    contents = bundle / "Contents"
    contents.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.info_plist, contents / "Info.plist")

    # Place the emacs binary at Contents/MacOS/Emacs.
    macos = contents / "MacOS"
    macos.mkdir(parents=True, exist_ok=True)
    target = macos / "Emacs"
    if target.exists():
        target.unlink()
    shutil.copy2(args.emacs_binary, target)
    target.chmod(0o755)

    # Self-contained layout.
    if args.self_contained:
        resources = contents / "Resources"
        resources.mkdir(parents=True, exist_ok=True)
        if args.lisp_dir is not None and args.lisp_dir.is_dir():
            copytree(args.lisp_dir, resources / "lisp")
        if args.etc_dir is not None and args.etc_dir.is_dir():
            copytree(args.etc_dir, resources / "etc")
        if args.info_dir is not None and args.info_dir.is_dir():
            info_dst = resources / "info"
            info_dst.mkdir(parents=True, exist_ok=True)
            for info in args.info_dir.glob("*.info"):
                shutil.copy2(info, info_dst / info.name)
        if args.pdmp is not None and args.pdmp.exists():
            libexec = contents / "MacOS" / "libexec"
            libexec.mkdir(parents=True, exist_ok=True)
            shutil.copy2(args.pdmp, libexec / "Emacs.pdmp")

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
