#!/usr/bin/env python3
"""Run a single ERT test file via the dumped emacs.

Mirrors the per-file pattern in test/Makefile.in:81 -- selector
defaults to (not (or (tag :expensive-test) (tag :unstable))) so
slow / known-flaky tests are excluded.  See
.claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_SELECTOR = "(not (or (tag :expensive-test) (tag :unstable)))"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emacs", required=True,
                   help="path to the dumped emacs binary")
    p.add_argument("--dump-file", required=True,
                   help="path to emacs.pdmp")
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--test-file", required=True, type=Path)
    p.add_argument("--selector", default=DEFAULT_SELECTOR)
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp_root = src_root / "lisp"
    test_root = src_root / "test"

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    # Build load path recursively (see byte_compile_batch.py).
    # emacs-lisp must come right after lisp/ root so the core
    # 'debug feature resolves to lisp/emacs-lisp/debug, not
    # lisp/cedet/semantic/debug.  Unlike byte_compile_batch.py,
    # do NOT skip obsolete/ -- tests in test/lisp/obsolete/ need
    # lisp/obsolete/ on the path.
    paths = [str(lisp_root), str(lisp_root / "emacs-lisp")]
    seen = {"emacs-lisp"}
    for d in sorted(lisp_root.rglob("*")):
        if not d.is_dir():
            continue
        rel = d.relative_to(lisp_root).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        paths.append(str(d))
    # Test directory itself + test file's parent for sibling helpers.
    paths.append(str(test_root))
    paths.append(str(args.test_file.parent))
    env["EMACSLOADPATH"] = ":".join(paths)

    selector = os.environ.get("EMACS_TEST_SELECTOR", args.selector)

    cmd = [
        args.emacs,
        "--batch",
        "-Q",
        f"--dump-file={args.dump_file}",
        "--eval", "(require (quote ert))",
        "-l", str(args.test_file),
        "--eval",
        f"(ert-run-tests-batch-and-exit (quote {selector}))",
    ]
    return subprocess.run(cmd, env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
