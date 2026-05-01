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

    # meson sets MESON_INSTALL_PREFIX (the configured prefix without
    # any DESTDIR) and MESON_INSTALL_DESTDIR_PREFIX (the staging path
    # = DESTDIR + prefix when DESTDIR is in scope).
    install_prefix = Path(
        os.environ.get("MESON_INSTALL_PREFIX", args.prefix)
    )
    destdir_prefix = Path(
        os.environ.get("MESON_INSTALL_DESTDIR_PREFIX", args.prefix)
    ).resolve()

    # Resolve a configured directory under the staging root, honouring
    # DESTDIR for absolute paths too.  When DIR is absolute, strip the
    # configured prefix and re-anchor under destdir_prefix; otherwise
    # treat DIR as prefix-relative and join.  Falls back to the raw
    # absolute path only when the configured prefix is not a parent
    # (e.g. a developer passed --bindir=/tmp/elsewhere on purpose).
    def resolve(p: str) -> Path:
        path = Path(p)
        if not path.is_absolute():
            return destdir_prefix / p
        try:
            rel = path.relative_to(install_prefix)
        except ValueError:
            return path
        return destdir_prefix / rel

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
