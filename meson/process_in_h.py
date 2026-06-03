#!/usr/bin/env python3
"""Substitute gnulib *.in.h variables, defaulting unset @VAR@ to 0.

gnulib in.h files contain dozens or hundreds of @VAR@ placeholders
(GNULIB_FOO, REPLACE_FOO, HAVE_DECL_FOO, ...).  In the autotools build
each one is set to 0 or 1 by an m4 macro, with most defaulting to 0
on systems where the libc already provides the function.

We replicate that behaviour here.  The caller supplies a small set of
overrides (typically the substitutions specific to the header, plus
the standard PRAGMA_SYSTEM_HEADER / INCLUDE_NEXT / NEXT_FOO_H trio);
every other @VAR@ found in the input is replaced with 0.

This is a transitional shim during the Meson migration.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_VAR = re.compile(r"@([A-Za-z_][A-Za-z0-9_]*)@")

def substitute(text: str, overrides: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name in overrides:
            return overrides[name]
        return "0"

    return _VAR.sub(repl, text)

# Marker comments that gnulib's sed scripts use to splice in helper
# header bodies (see lib/gnulib.mk.in:3872-3874).
_INSERTS = [
    ("definitions of _GL_FUNCDECL_RPL", "c++defs.h"),
    ("definition of _GL_ARG_NONNULL", "arg-nonnull.h"),
    ("definition of _GL_WARN_ON_USE", "warn-on-use.h"),
]

def insert_snippets(text: str, lib_dir: Path) -> str:
    """Mimic sed's `/MARKER/r FILE` behaviour for gnulib snippet headers."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        out.append(line)
        for marker, fname in _INSERTS:
            if marker in line:
                snippet_path = lib_dir / fname
                if snippet_path.exists():
                    snippet = snippet_path.read_text()
                    if not snippet.endswith("\n"):
                        snippet += "\n"
                    out.append(snippet)
    return "".join(out)

def _append_assert_static_assert(text: str, lib_dir: Path) -> str:
    verify = (lib_dir / "verify.h").read_text()
    verify = re.sub(r"/\*@assert\.h omit start@\*/.*?/\*@assert\.h omit end@\*/\n?", "", verify, flags=re.S)
    verify = verify.replace("_gl_verify", "_gl_static_assert")
    verify = verify.replace("_GL_VERIFY", "_GL_STATIC_ASSERT")
    verify = re.sub(r"_GL\((_STATIC_ASSERT_H)\)", r"_GL\1", verify)
    if not text.endswith("\n"):
        text += "\n"
    if not verify.endswith("\n"):
        verify += "\n"
    return text + verify

def _rewrite_ieee754_guard(text: str) -> str:
    return text.replace("#ifndef _GL_GNULIB_HEADER", "#if 0", 1)

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="override variable NAME with VALUE (may be repeated)",
    )
    p.add_argument(
        "--json",
        type=Path,
        help="JSON file mapping variable names to override values",
    )
    p.add_argument("--append-assert-verify", action="store_true",
                   help="append transformed verify.h body used by assert.h rule")
    p.add_argument("--rewrite-ieee754-guard", action="store_true",
                   help="rewrite ieee754.in.h gnulib guard to #if 0")

    p.add_argument(
        "--lib-dir",
        type=Path,
        help=(
            "directory containing gnulib snippet headers (c++defs.h, "
            "arg-nonnull.h, warn-on-use.h) for sed-style inclusion"
        ),
    )
    args = p.parse_args()

    overrides: dict[str, str] = {}
    if args.json is not None:
        overrides.update(json.loads(args.json.read_text()))
    for entry in args.set:
        if "=" not in entry:
            print(f"--set expects NAME=VALUE, got {entry!r}", file=sys.stderr)
            return 2
        k, v = entry.split("=", 1)
        overrides[k] = v

    src = args.input.read_text()
    out = substitute(src, overrides)
    if args.lib_dir is not None:
        out = insert_snippets(out, args.lib_dir)
    if args.rewrite_ieee754_guard:
        out = _rewrite_ieee754_guard(out)
    if args.append_assert_verify:
        if args.lib_dir is None:
            print("--append-assert-verify requires --lib-dir", file=sys.stderr)
            return 2
        out = _append_assert_static_assert(out, args.lib_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
