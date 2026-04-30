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
    # Test files in test/lisp/foo-tests.el load lisp/foo.el; need
    # the lisp/ tree on load-path.  Plus the test directory itself
    # so test/foo-tests.el can require sibling helpers.
    paths = [str(lisp_root)] + sorted(
        str(p) for p in lisp_root.iterdir() if p.is_dir()
    )
    paths.append(str(test_root))
    paths.append(str(args.test_file.parent))
    env["EMACSLOADPATH"] = ":".join(paths)

    cmd = [
        args.emacs,
        "--batch",
        "-Q",
        f"--dump-file={args.dump_file}",
        "--eval", "(require (quote ert))",
        "-l", str(args.test_file),
        "--eval",
        f"(ert-run-tests-batch-and-exit (quote {args.selector}))",
    ]
    return subprocess.run(cmd, env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
