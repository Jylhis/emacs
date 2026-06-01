#!/usr/bin/env python3
"""Native-compile every byte-compiled .elc into a .eln.

Mirrors the autotools rule in lisp/Makefile.in:446-449:

    %.eln: %.el
        ${emacs} -l comp -f byte-compile-refresh-preloaded \\
            --eval '(batch-native-compile t)' $<

Driven once over the full lisp tree, taking the .el list from a
manifest (matches our byte-compile path).  Skips files annotated
``no-native-compile: t`` (Makefile.in:466).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

NO_NATIVE_RE = re.compile(rb"^;.*[^a-zA-Z]no-native-compile:\s*t", re.MULTILINE)
NO_BYTE_RE = re.compile(rb"^;.*[^a-zA-Z]no-byte-compile:\s*t", re.MULTILINE)

def skipworthy(el: Path) -> bool:
    head = el.read_bytes()[:4096]
    return bool(NO_NATIVE_RE.search(head) or NO_BYTE_RE.search(head))

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emacs", required=True,
                   help="path to the dumped emacs binary")
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--lisp-dir", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path,
                   help="newline-separated list of .el paths (rel to lisp-dir)")
    p.add_argument("--stamp", required=True, type=Path)
    p.add_argument("--chunk-size", type=int, default=20)
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp_root = args.lisp_dir.resolve()
    rel_files = [Path(line.strip())
                 for line in args.manifest.read_text().splitlines()
                 if line.strip()]
    work = []
    for rel in rel_files:
        el = lisp_root / rel
        if not el.exists():
            continue
        if skipworthy(el):
            continue
        work.append(el)
    print(f"native-compiling {len(work)} files (skipped "
          f"{len(rel_files) - len(work)} no-native-compile/no-byte-compile)",
          file=sys.stderr, flush=True)

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")

    base = [
        args.emacs,
        "--batch", "--no-site-file", "--no-site-lisp",
        "-l", "comp",
        "-f", "byte-compile-refresh-preloaded",
        "--eval", "(batch-native-compile t)",
    ]
    chunk_size = args.chunk_size
    total_chunks = (len(work) + chunk_size - 1) // chunk_size
    failed_chunks: list[int] = []
    for i in range(0, len(work), chunk_size):
        idx = i // chunk_size + 1
        chunk = work[i:i + chunk_size]
        cmd = base + [str(el) for el in chunk]
        rc = subprocess.run(cmd, env=env).returncode
        if rc != 0:
            print(f"chunk {idx} rc={rc}; continuing", file=sys.stderr, flush=True)
            failed_chunks.append(idx)

    # Record outcome in the stamp so a rebuild that wants to retry
    # failed chunks can read which ones to redo.  Returning non-zero
    # surfaces the failure to Meson so the .eln cache is not treated
    # as a successful artefact; CI gates this step with
    # continue-on-error today (see .github/workflows/meson.yml).
    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    if failed_chunks:
        args.stamp.write_text(
            "failed: " + " ".join(str(c) for c in failed_chunks) + "\n"
        )
        print(f"{len(failed_chunks)}/{total_chunks} chunks failed",
              file=sys.stderr, flush=True)
        return 1
    args.stamp.write_text("ok\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
