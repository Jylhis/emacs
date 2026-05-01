#!/usr/bin/env python3
"""Generate src/emacs-module.h from src/emacs-module.in.h.

The autotools build substitutes @emacs_major_version@ and AC_SUBST_FILE
placeholders @module_env_snippet_NN@ with the contents of
src/module-env-NN.h (configure.ac:4438-4452).  We replicate that here.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_SUBST_FILE = re.compile(r"^@(module_env_snippet_\d+)@\s*$", re.MULTILINE)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--src-dir", type=Path, required=True,
                   help="directory containing module-env-NN.h files")
    p.add_argument("--major-version", required=True)
    args = p.parse_args()

    text = args.input.read_text()
    text = text.replace("@emacs_major_version@", args.major_version)

    def subst_file(m: re.Match[str]) -> str:
        snippet = m.group(1)
        # snippet looks like 'module_env_snippet_25'
        n = snippet.rsplit("_", 1)[1]
        path = args.src_dir / f"module-env-{n}.h"
        if not path.exists():
            return ""
        body = path.read_text()
        if not body.endswith("\n"):
            body += "\n"
        return body

    text = _SUBST_FILE.sub(subst_file, text)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
