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


EXCLUDED_DIRS = {"obsolete", "term", "leim/quail"}


def stage_intl(lisp: Path, charscript: Path | None,
               emoji_zwj: Path | None) -> None:
    """Stage admin/-generated files into lisp/international/ so
    bootstrap-emacs's loadup.el can `(require 'charscript)` etc."""
    import shutil
    intl = lisp / "international"
    intl.mkdir(parents=True, exist_ok=True)
    for staged, fname in [
        (charscript, "charscript.el"),
        (emoji_zwj, "emoji-zwj.el"),
    ]:
        if staged is None or not staged.exists():
            continue
        target = intl / fname
        if not target.exists() or target.read_bytes() != staged.read_bytes():
            shutil.copy2(staged, target)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--stamp", required=True, type=Path)
    p.add_argument("--charscript", type=Path)
    p.add_argument("--emoji-zwj", type=Path)
    p.add_argument("--subdirs", nargs="*", default=[],
                   help="(deprecated) ignored -- subdirs are auto-enumerated")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp = src_root / "lisp"
    stage_intl(lisp, args.charscript, args.emoji_zwj)

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    # Explicitly enumerate lisp/ subdirs in EMACSLOADPATH because we
    # don't generate subdirs.el in the build tree.  The autotools
    # build's `make update-subdirs` does populate them; we'll wire
    # that via a separate subdirs.el target later.
    paths = [str(lisp)] + sorted(
        str(p) for p in lisp.iterdir() if p.is_dir()
    )
    env["EMACSLOADPATH"] = ":".join(paths)

    # Enumerate every subdirectory of lisp/ except the ones autotools'
    # SUBDIRS_ALMOST excludes (obsolete/, term/) and a few that don't
    # need autoloads (leim/quail/ -- Quail input methods are linked
    # via leim-list.el, not loaddefs).  Mirrors lisp/Makefile.in:121.
    dirs = [str(lisp)]
    for d in sorted(lisp.rglob("*")):
        if not d.is_dir():
            continue
        rel = d.relative_to(lisp).as_posix()
        if rel in EXCLUDED_DIRS or any(
            rel == ex or rel.startswith(ex + "/") for ex in EXCLUDED_DIRS
        ):
            continue
        dirs.append(str(d))

    cmd = [
        args.bootstrap_emacs,
        "--batch", "--no-site-file", "--no-site-lisp",
        "-l", str(lisp / "emacs-lisp/loaddefs-gen.el"),
        "-f", "loaddefs-generate--emacs-batch",
    ] + dirs

    rc = subprocess.run(cmd, env=env).returncode
    if rc != 0:
        return rc

    # Touch top-level loaddefs.el so it has the newest mtime among
    # all loaddefs.el files in the tree.  loaddefs-generate writes
    # cedet/ede/loaddefs.el etc. in addition to lisp/loaddefs.el, and
    # both `(provide 'loaddefs)`.  When byte-compile sets
    # load-prefer-newer, `(load "loaddefs")` from loadup.el would
    # otherwise pick whichever was written last -- typically a
    # subdir-specific one, which assumes eieio-core is loaded.
    import time
    main = lisp / "loaddefs.el"
    if main.exists():
        now = time.time()
        os.utime(main, (now, now))

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
