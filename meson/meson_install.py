#!/usr/bin/env python3
"""Install emacs binary, dump image, lisp/, and etc/ into DESTDIR.

Replaces the autotools `make install` recipes (Makefile.in:552-937)
in their bare minimum form: emacs binary, emacs.pdmp, lisp tree,
etc tree.  Desktop, icon, info, gsettings, man pages land later.

meson.add_install_script invokes this with absolute prefix paths
already adjusted for DESTDIR (meson sets MESON_INSTALL_DESTDIR_PREFIX
in environment).  See
.claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def copytree(src: Path, dst: Path, *, exclude: set[str] | None = None) -> None:
    exclude = exclude or set()
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        # Filter out excluded directories in-place so os.walk skips them.
        dirs[:] = [d for d in dirs if d not in exclude]
        out = dst / rel
        out.mkdir(parents=True, exist_ok=True)
        for f in files:
            if f in exclude:
                continue
            shutil.copy2(Path(root) / f, out / f)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prefix", required=True)
    p.add_argument("--bindir", required=True)
    p.add_argument("--datadir", required=True,
                   help="emacs share dir, e.g. share/emacs/31.0.50")
    p.add_argument("--libexecdir", required=True,
                   help="arch-specific dir holding emacs.pdmp")
    p.add_argument("--build-root", required=True, type=Path)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--version", required=True)
    args = p.parse_args()

    # meson exports DESTDIR-adjusted paths via MESON_INSTALL_DESTDIR_PREFIX.
    destdir_prefix = os.environ.get(
        "MESON_INSTALL_DESTDIR_PREFIX", args.prefix
    )
    destdir = Path(destdir_prefix).resolve()

    # bindir / libexecdir / datadir come in as $prefix-relative; if they
    # are absolute we treat them as-is, otherwise prepend destdir.
    def resolve(p: str) -> Path:
        path = Path(p)
        if path.is_absolute():
            # honour DESTDIR by stripping the prefix prefix and
            # rebasing.  meson.add_install_script's argv-based prefix
            # already includes destdir prefix when meson handles it,
            # so just keep absolute paths.
            return path
        return destdir / p

    bindir = resolve(args.bindir)
    libexecdir = resolve(args.libexecdir)
    datadir = resolve(args.datadir)

    bindir.mkdir(parents=True, exist_ok=True)
    libexecdir.mkdir(parents=True, exist_ok=True)
    datadir.mkdir(parents=True, exist_ok=True)

    # emacs binary -- as emacs-VERSION + an emacs symlink.
    emacs_bin = args.build_root / "src/emacs"
    if emacs_bin.exists():
        target = bindir / f"emacs-{args.version}"
        shutil.copy2(emacs_bin, target)
        target.chmod(0o755)
        link = bindir / "emacs"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(target.name)
    else:
        print(f"warning: {emacs_bin} not built; skipping emacs install",
              file=sys.stderr)

    # emacs.pdmp goes into libexec/emacs/VERSION/ARCH/.
    pdmp = args.build_root / "src/emacs.pdmp"
    if pdmp.exists():
        shutil.copy2(pdmp, libexecdir / "emacs.pdmp")

    # lisp tree -- read-only data, .el and .elc.
    lisp_src = args.source_root / "lisp"
    lisp_dst = datadir / "lisp"
    if lisp_src.is_dir():
        copytree(lisp_src, lisp_dst,
                 exclude={"__pycache__", "Makefile.in", "Makefile"})

    # etc tree -- charsets, images, tutorials, NEWS, etc.
    etc_src = args.source_root / "etc"
    etc_dst = datadir / "etc"
    if etc_src.is_dir():
        copytree(etc_src, etc_dst, exclude={"__pycache__"})

    print(f"installed emacs {args.version} into {destdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
