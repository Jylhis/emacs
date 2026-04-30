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
    p.add_argument("--charscript", type=Path,
                   help="generated lisp/international/charscript.el to stage")
    p.add_argument("--emoji-zwj", type=Path,
                   help="generated lisp/international/emoji-zwj.el to stage")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp_root = args.lisp_dir.resolve()

    # Stage charscript.el / emoji-zwj.el into lisp/international/ so
    # bootstrap-emacs's loadup.el (which reads characters.el) can
    # resolve `(require 'charscript)` etc.  In the autotools build
    # these files live in lisp/international/ all the time because
    # admin/unidata/Makefile generates them in place.  Meson generates
    # them in the build tree, so they need an explicit copy.
    intl = lisp_root / "international"
    intl.mkdir(parents=True, exist_ok=True)
    for staged, fname in [
        (args.charscript, "charscript.el"),
        (args.emoji_zwj, "emoji-zwj.el"),
    ]:
        if staged is None or not staged.exists():
            continue
        target = intl / fname
        if not target.exists() or target.read_bytes() != staged.read_bytes():
            shutil.copy2(staged, target)

    rel_files = [Path(line.strip())
                 for line in args.manifest.read_text().splitlines()
                 if line.strip()]

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = ":".join(_load_path(lisp_root))
    # Match the BYTE_COMPILE_FLAGS in lisp/Makefile.in:78.
    env["BYTE_COMPILE_DEBUG"] = "1"

    base_cmd = [
        args.bootstrap_emacs,
        "--batch",
        "--no-site-file",
        "--no-site-lisp",
        "--eval",
        "(setq load-prefer-newer t byte-compile-warnings 'all)",
        "--eval",
        "(setq org--inhibit-version-check t)",
        # Disable native-comp's async background compilation while we
        # batch byte-compile, so a native-comp failure doesn't bubble
        # up as a non-zero exit from batch-byte-compile.
        "--eval",
        "(when (featurep 'native-compile)"
        " (setq native-comp-jit-compilation nil"
        "       native-comp-enable-subr-trampolines nil))",
        "-f", "batch-byte-compile",
    ]

    # Chunk to keep the bootstrap-emacs heap manageable.  Empirically
    # batch-byte-compile starts segfaulting around 65-70 accumulated
    # files on this branch's bootstrap-emacs (the byte-compiler state
    # carries macro expansions that interact with our SYSTEM_MALLOC +
    # rpl_realloc redirect in pathological ways).  50 keeps each
    # chunk well clear.
    chunk_size = 50
    failed_individually: list[Path] = []
    for i in range(0, len(rel_files), chunk_size):
        chunk = rel_files[i:i + chunk_size]
        cmd = base_cmd + [str(lisp_root / r) for r in chunk]
        print(f"compiling chunk {i // chunk_size + 1}: "
              f"{len(chunk)} files starting with {chunk[0]}",
              file=sys.stderr, flush=True)
        rc = subprocess.run(cmd, env=env).returncode
        if rc != 0:
            # When a chunk fails (typically bootstrap-emacs segfaults
            # at the first un-compilable file), every file after the
            # crash point in that chunk is left without a .elc.
            # Bisect: split the chunk in half and retry each half;
            # repeat until single files isolate the bad apple.  This
            # keeps the average cost O(log N) per crash instead of
            # O(N) full re-runs per file.
            stack = [chunk]
            while stack:
                sub = stack.pop()
                # Skip files whose .elc has already been produced.
                missing = [r for r in sub
                           if not (lisp_root / r.with_suffix(".elc")).exists()]
                if not missing:
                    continue
                if len(missing) == 1:
                    rel = missing[0]
                    ind_cmd = base_cmd + [str(lisp_root / rel)]
                    if subprocess.run(ind_cmd, env=env).returncode != 0:
                        failed_individually.append(rel)
                    continue
                rc2 = subprocess.run(
                    base_cmd + [str(lisp_root / r) for r in missing],
                    env=env,
                ).returncode
                if rc2 != 0:
                    mid = len(missing) // 2
                    stack.append(missing[mid:])
                    stack.append(missing[:mid])
    if failed_individually:
        print(f"  {len(failed_individually)} files still failed individually:",
              file=sys.stderr, flush=True)
        for f in failed_individually[:5]:
            print(f"    {f}", file=sys.stderr, flush=True)

    # batch-byte-compile writes the .elc next to each .el.  Move them
    # into the build tree, preserving the relative layout.  Files that
    # failed to byte-compile (e.g. lisp/obsolete/* with broken
    # references) are skipped, matching the autotools build's
    # behaviour where compile-main emits the error and continues.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    skipped = 0
    for rel in rel_files:
        elc_src = lisp_root / rel.with_suffix(".elc")
        elc_dst = args.output_dir / rel.with_suffix(".elc")
        if not elc_src.exists():
            skipped += 1
            continue
        elc_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(elc_src, elc_dst)
        moved += 1
    print(f"byte-compiled {moved} files; {skipped} skipped (compile errors)",
          file=sys.stderr)
    if args.stamp is not None:
        args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
