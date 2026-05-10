#!/usr/bin/env python3
"""Run bootstrap-emacs to regenerate Quail input-method tables.

Mirrors the autotools rules in leim/Makefile.in at anchor commit
08a22b8965ec.  The generated *.el files land in the source tree
(lisp/leim/quail/ and lisp/leim/ja-dic/) because byte-compile,
loaddefs extraction, and the final pdumper image expect them
there.

Three modes:

  --tit DIR      Run titdic-cnv batch-tit-dic-convert against every
                 *.tit under DIR.

  --misc DIR     Run titdic-cnv batch-tit-miscdic-convert against
                 each MISC-DIC source file (HTML / .map / .cin /
                 cangjie-table.* are mapped to their CTLau /
                 PY / ZIRANMA / tsang / quick outputs).

  --pinyin SRC   Run tit-pinyin-convert against MISC-DIC/pinyin.map,
                 producing lisp/language/pinyin.el.

  --skk-dic SRC  Run ja-dic-cnv batch-skkdic-convert against
                 SKK-DIC/SKK-JISYO.L, producing lisp/leim/ja-dic/.

  --leim-list    Run quail update-leim-list-file over lisp/leim/ and
                 append the inc-suffixed lines from leim-ext.el.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _env(src_root: Path) -> dict:
    env = os.environ.copy()
    lisp = src_root / "lisp"
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    # Mirror run_loaddefs.py: enumerate lisp subdirs so titdic-cnv's
    # `(require 'international/quail)` etc. resolves under -batch.
    paths = [str(lisp)] + sorted(
        str(p) for p in lisp.iterdir() if p.is_dir()
    )
    env["EMACSLOADPATH"] = ":".join(paths)
    return env


def _run(cmd: list, env: dict, cwd: Path | None = None) -> int:
    print("running:", " ".join(str(x) for x in cmd), flush=True)
    return subprocess.run(cmd, env=env, cwd=cwd).returncode


def _emacs_cmd(args) -> list:
    cmd = [args.bootstrap_emacs]
    if args.dump_file:
        cmd.append(f"--dump-file={args.dump_file}")
    cmd += ["--batch", "--no-site-file", "--no-site-lisp"]
    return cmd


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True)
    p.add_argument("--dump-file", default="")
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--stamp", required=True, type=Path)

    sub = p.add_mutually_exclusive_group(required=True)
    sub.add_argument("--tit", type=Path,
                     help="CXTERM-DIC directory; convert *.tit to "
                          "lisp/leim/quail/*.el")
    sub.add_argument("--misc", type=Path,
                     help="MISC-DIC directory; convert HTML/map/cin "
                          "files to lisp/leim/quail/*.el")
    sub.add_argument("--pinyin", type=Path,
                     help="path to MISC-DIC/pinyin.map; produces "
                          "lisp/language/pinyin.el")
    sub.add_argument("--skk-dic", type=Path,
                     help="path to SKK-DIC/SKK-JISYO.L; produces "
                          "lisp/leim/ja-dic/ja-dic.el")
    sub.add_argument("--leim-list", action="store_true",
                     help="generate lisp/leim/leim-list.el")

    p.add_argument("--small-ja-dic", action="store_true",
                   help="omit --no-reduction when generating ja-dic")
    p.add_argument("--leim-ext", type=Path,
                   help="path to leim/leim-ext.el (for --leim-list)")

    args = p.parse_args()

    src_root = args.source_root.resolve()
    leim_dir = src_root / "lisp/leim"
    quail_dir = leim_dir / "quail"
    ja_dic_dir = leim_dir / "ja-dic"
    env = _env(src_root)

    quail_dir.mkdir(parents=True, exist_ok=True)
    ja_dic_dir.mkdir(parents=True, exist_ok=True)

    if args.tit is not None:
        tits = sorted(args.tit.glob("*.tit"))
        if not tits:
            print(f"no *.tit files found in {args.tit}", file=sys.stderr)
            return 1
        cmd = _emacs_cmd(args) + [
            "-l", "titdic-cnv",
            "-f", "batch-tit-dic-convert",
            "-dir", str(quail_dir),
        ] + [str(t) for t in tits]
        rc = _run(cmd, env)
        if rc != 0:
            return rc

    elif args.misc is not None:
        # The MISC-DIC sources land in lisp/leim/quail/ via a single
        # batch-tit-miscdic-convert pass; the function dispatches by
        # file extension internally (see leim/titdic-cnv.el).
        misc_files = []
        for pat in ("CTLau*.html", "*.map", "*.cin", "cangjie-table.*"):
            misc_files.extend(sorted(args.misc.glob(pat)))
        if not misc_files:
            print(f"no MISC-DIC files found in {args.misc}",
                  file=sys.stderr)
            return 1
        cmd = _emacs_cmd(args) + [
            "-l", "titdic-cnv",
            "-f", "batch-tit-miscdic-convert",
            "-dir", str(quail_dir),
        ] + [str(f) for f in misc_files]
        rc = _run(cmd, env)
        if rc != 0:
            return rc

    elif args.pinyin is not None:
        out = src_root / "lisp/language/pinyin.el"
        cmd = _emacs_cmd(args) + [
            "-l", "titdic-cnv",
            "-f", "tit-pinyin-convert",
            str(args.pinyin), str(out),
        ]
        rc = _run(cmd, env)
        if rc != 0:
            return rc

    elif args.skk_dic is not None:
        cmd = _emacs_cmd(args) + [
            "-l", "ja-dic-cnv",
            "-f", "batch-skkdic-convert",
            "-dir", str(ja_dic_dir),
        ]
        if not args.small_ja_dic:
            cmd.append("--no-reduction")
        cmd.append(str(args.skk_dic))
        rc = _run(cmd, env)
        if rc != 0:
            return rc

    elif args.leim_list:
        # Step 1: emacs --batch -l international/quail \
        #              --eval '(update-leim-list-file LEIMDIR)'
        out = leim_dir / "leim-list.el"
        if out.exists():
            out.unlink()
        cmd = _emacs_cmd(args) + [
            "-l", "international/quail",
            "--eval",
            f"(update-leim-list-file {json.dumps(str(leim_dir))})",
        ]
        rc = _run(cmd, env)
        if rc != 0:
            return rc
        # Step 2: append inc-suffixed lines from leim-ext.el
        # (mirror leim/Makefile.in's sed pipeline:
        #  sed -n -e '/^[^;]/p' -e 's/^;\(;*\)inc /;\1 /p').
        if args.leim_ext is not None and args.leim_ext.exists():
            with args.leim_ext.open() as fin, out.open("a") as fout:
                for line in fin:
                    stripped = line.lstrip()
                    if stripped and not stripped.startswith(";"):
                        fout.write(line)
                    elif stripped.startswith(";"):
                        # Match lines starting with ";" + 0+ ";" + "inc "
                        # and turn the "inc " into a single space.
                        i = 0
                        while i < len(stripped) and stripped[i] == ";":
                            i += 1
                        rest = stripped[i:]
                        if rest.startswith("inc "):
                            fout.write(
                                ";" * i + " " + rest[len("inc "):]
                            )

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
