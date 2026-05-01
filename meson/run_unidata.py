#!/usr/bin/env python3
"""Generate lisp/international/uni-*.el and charprop.el via bootstrap-emacs.

Mirrors admin/unidata/Makefile.in's recipes that invoke
``${EMACS} -L admin/unidata -l unidata-gen -f unidata-gen-file FILE DIR``
and ``... -f unidata-gen-charprop FILE``.  Bootstrap-emacs (undumped
temacs) is sufficient because unidata-gen.el is documented to be
runnable by temacs, and loadup.el detects the unidata-gen mode and
sets up load-path without dumping.

See .claude/plans/migrate-from-current-build-replicated-gadget.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


# uni-*.el files listed in unidata-gen.el's unidata-file-alist.  Parsed
# from the source so we don't drift if upstream adds entries.
def discover_uni_files(unidata_gen_el: Path) -> list[str]:
    text = unidata_gen_el.read_text(encoding="utf-8")
    pat = re.compile(r'^\s*\("(uni-[^"]+\.el)"', re.MULTILINE)
    return pat.findall(text)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True,
                   help="path to bootstrap-emacs binary")
    p.add_argument("--dump-file", type=Path,
                   help="bootstrap-emacs.pdmp; lets bootstrap-emacs run "
                        "as the dumped emacs (undumped temacs segfaults "
                        "on the unidata-gen workload).")
    p.add_argument("--source-root", required=True, type=Path,
                   help="path to Emacs source root")
    p.add_argument("--stamp", required=True, type=Path,
                   help="stamp file written on success")
    p.add_argument("--charscript", type=Path,
                   help="generated charscript.el to stage in lisp/international/")
    p.add_argument("--emoji-zwj", type=Path,
                   help="generated emoji-zwj.el to stage in lisp/international/")
    args = p.parse_args()

    src_root = args.source_root.resolve()
    unidata_dir = src_root / "admin/unidata"
    intl_dir = src_root / "lisp/international"
    intl_dir.mkdir(parents=True, exist_ok=True)

    # Stage charscript.el / emoji-zwj.el so bootstrap-emacs's
    # loadup.el can `(require 'charscript)` while running unidata-gen.
    import shutil
    for staged, fname in [
        (args.charscript, "charscript.el"),
        (args.emoji_zwj, "emoji-zwj.el"),
    ]:
        if staged is None or not staged.exists():
            continue
        target = intl_dir / fname
        if not target.exists() or target.read_bytes() != staged.read_bytes():
            shutil.copy2(staged, target)

    uni_files = discover_uni_files(unidata_dir / "unidata-gen.el")
    if not uni_files:
        print("error: no uni-*.el entries found in unidata-gen.el",
              file=sys.stderr)
        return 1

    # Generate unidata.txt -- `unidata-gen-file` reads this rather
    # than UnicodeData.txt directly.  Mirrors the sed pipeline at
    # admin/unidata/Makefile.in:64-65.
    unicode_data = unidata_dir / "UnicodeData.txt"
    args.stamp = args.stamp.resolve()
    unidata_txt = (args.stamp.parent / "unidata.txt").resolve()
    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    with unidata_txt.open("w", encoding="utf-8") as out:
        for line in unicode_data.read_text(encoding="utf-8").splitlines():
            head, sep, rest = line.partition(";")
            if not sep:
                continue
            transformed = '(#x' + head + ' "' + rest.replace(";", '" "') + '")'
            out.write(transformed + "\n")

    # Bootstrap-emacs runs from src/ so PATH_DUMPLOADSEARCH = "../lisp"
    # resolves correctly.  unidata-gen-file uses `default-directory` /
    # the data-dir argument to find UnicodeData.txt etc.
    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = str(src_root / "lisp")

    base_cmd = [args.bootstrap_emacs]
    if args.dump_file is not None:
        base_cmd.append(f"--dump-file={args.dump_file}")
    base_cmd += [
        "--batch", "--no-site-file", "--no-site-lisp",
        "-L", str(unidata_dir),
        "-l", "unidata-gen",
    ]

    # Generate each uni-*.el file in lisp/international/.
    for fname in uni_files:
        out = intl_dir / fname
        if out.exists():
            continue
        cmd = base_cmd + [
            "-f", "unidata-gen-file",
            str(out), str(unidata_dir), str(unidata_txt),
        ]
        print(f"generating {out.relative_to(src_root)}", flush=True)
        rc = subprocess.run(cmd, cwd=src_root / "src", env=env).returncode
        if rc != 0:
            return rc

    # Generate charprop.el.
    charprop = intl_dir / "charprop.el"
    if not charprop.exists():
        cmd = base_cmd + [
            "-f", "unidata-gen-charprop", str(charprop),
        ]
        print(f"generating {charprop.relative_to(src_root)}", flush=True)
        rc = subprocess.run(cmd, cwd=src_root / "src", env=env).returncode
        if rc != 0:
            return rc

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
