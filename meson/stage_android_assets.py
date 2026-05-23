#!/usr/bin/env python3
"""Stage Emacs runtime assets for the Android APK.

Copies byte-compiled Lisp, etc/, info/, and the pdumper image from a
completed host meson build into a staging tree that the APK packager
(aapt2) embeds under assets/.

Inputs:
  --host-build     Path to a host meson build dir (must contain
                   src/emacs.pdmp and the byte-compiled lisp tree).
  --source-root    Path to the Emacs source tree (provides etc/, info/).
  --output         Destination staging directory; created (or wiped)
                   and populated.
  --stamp          Stamp file written on success.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        sys.stderr.write(f"stage_android_assets: missing source {src}\n")
        sys.exit(1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host-build", required=True, type=Path)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--stamp", required=True, type=Path)
    args = p.parse_args()

    host_build = args.host_build.resolve()
    source_root = args.source_root.resolve()
    output = args.output.resolve()

    pdmp = host_build / "src" / "emacs.pdmp"
    if not pdmp.exists():
        sys.stderr.write(
            "stage_android_assets: host build is incomplete; "
            f"expected {pdmp} -- run `meson compile -C {host_build}` "
            "to build the host emacs first.\n"
        )
        return 1

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    # Byte-compiled Lisp: prefer the host build's lisp tree (already
    # has uni-*.el / charprop.el / loaddefs.el produced by the
    # bootstrap), but the .el / .elc files themselves come from the
    # source tree for .el and the build tree for .elc.
    src_lisp = source_root / "lisp"
    dst_lisp = output / "lisp"
    copy_tree(src_lisp, dst_lisp)
    # Overlay .elc files from the host build dir if they exist there.
    build_lisp = host_build / "lisp"
    if build_lisp.exists():
        for elc in build_lisp.rglob("*.elc"):
            rel = elc.relative_to(build_lisp)
            target = dst_lisp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(elc, target)

    # etc/ and info/.  info/ may not exist if the host build did not
    # produce manuals; that is acceptable for a minimal APK.
    copy_tree(source_root / "etc", output / "etc")
    info_src = host_build / "info"
    if info_src.exists():
        copy_tree(info_src, output / "info")

    # The pdumper image lives alongside the binary on desktop, but
    # the Android port loads it from assets via the APK's
    # AssetManager.
    shutil.copy2(pdmp, output / "emacs.pdmp")

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
