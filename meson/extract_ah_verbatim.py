#!/usr/bin/env python3
"""Extract AH_VERBATIM blocks from autoconf m4 files into a C header.

In the autotools build, gnulib-common.m4 contributes most of its content
to src/config.h via AH_VERBATIM([tag], [body]) blocks.  Meson does not
process m4 files, so we replicate that contribution by parsing the m4
file and writing the contents of every AH_VERBATIM block to a header
file that config.h includes.

This is a transitional shim used during the Meson migration; see
.claude/plans/migrate-from-current-build-replicated-gadget.md.

The body of an AH_VERBATIM call is m4-quoted and may be split into
several adjacent quoted segments connected by dnl comments, e.g.::

    AH_VERBATIM([tag],
    [...part 1...
    ]dnl explanatory comment
    [...part 2...
    ])

We collect every top-level ``[...]`` segment after the first comma and
concatenate them into a single body.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_OPEN = re.compile(r"\bAH_VERBATIM\s*\(\s*")


def _skip_quoted(text: str, start: int) -> int:
    """Return the index just after the matching ``]`` for the ``[`` at start."""
    assert text[start] == "["
    depth = 1
    i = start + 1
    while i < len(text):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError(f"unterminated [...] starting at offset {start}")


def _read_call(text: str, start: int) -> tuple[str, str, int]:
    """Parse a single AH_VERBATIM(...) starting at ``start``.

    Returns (tag, body, end_index).  ``end_index`` points at the first
    character after the closing ')'.
    """
    # Skip whitespace.
    i = start
    while i < len(text) and text[i].isspace():
        i += 1
    if text[i] != "[":
        raise ValueError(f"expected '[' for tag at offset {i}")
    tag_end = _skip_quoted(text, i)
    tag = text[i + 1 : tag_end - 1]

    # Skip ',' and whitespace.
    j = tag_end
    while j < len(text) and text[j] in " \t\n":
        j += 1
    if text[j] != ",":
        raise ValueError(f"expected ',' after tag at offset {j}")
    j += 1

    # Body: every top-level [...] segment until ')'.
    parts: list[str] = []
    while j < len(text):
        while j < len(text) and text[j] in " \t\n":
            j += 1
        if j >= len(text):
            break
        ch = text[j]
        if ch == ")":
            return tag, "".join(parts), j + 1
        if ch == "[":
            seg_end = _skip_quoted(text, j)
            parts.append(text[j + 1 : seg_end - 1])
            j = seg_end
            continue
        # Skip dnl comments and other top-level junk between segments.
        if text.startswith("dnl", j):
            nl = text.find("\n", j)
            j = nl + 1 if nl >= 0 else len(text)
            continue
        # Any other character at top level: skip it.  AH_VERBATIM bodies
        # don't usually contain unquoted text, but be permissive.
        j += 1
    raise ValueError("unterminated AH_VERBATIM call")


def extract(m4_path: Path) -> str:
    text = m4_path.read_text()
    out: list[str] = []
    for m in _OPEN.finditer(text):
        try:
            tag, body, _ = _read_call(text, m.end())
        except ValueError as exc:  # pragma: no cover -- debugging aid
            print(
                f"warning: skipping AH_VERBATIM at offset {m.start()}: {exc}",
                file=sys.stderr,
            )
            continue
        out.append(f"/* AH_VERBATIM([{tag}]) */\n{body.rstrip()}")
    return "\n\n".join(out) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output", type=Path, required=True, help="output C header"
    )
    p.add_argument("inputs", type=Path, nargs="+", help="input m4 files")
    args = p.parse_args()

    sections: list[str] = []
    sources: list[str] = []
    for src in args.inputs:
        sources.append(src.name)
        sections.append(f"/* === from {src.name} === */\n{extract(src)}")

    header_guard = "EMACS_GNULIB_COMMON_H"
    header = (
        f"/* Auto-generated from {', '.join(sources)} by\n"
        f"   meson/extract_ah_verbatim.py.  Do not edit by hand.  */\n"
        f"#ifndef {header_guard}\n"
        f"#define {header_guard} 1\n"
        f"\n"
        f"{chr(10).join(sections)}"
        f"\n#endif /* {header_guard} */\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(header)
    return 0


if __name__ == "__main__":
    sys.exit(main())
