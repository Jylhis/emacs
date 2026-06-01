#!/usr/bin/env python3
"""Generate CEDET parser files from the admin/grammars/ sources.

Ports admin/grammars/Makefile.in (removed at the autotools cutover).
Upstream stopped committing the generated grammars in
f9b697ddaa6 ("Stop keeping (all but one) generated cedet grammar files
in the repository"); they are produced at build time from the .wy
(wisent) and .by (bovine) sources via semantic's batch grammar
compilers:

    emacs -l semantic/bovine/grammar -f bovine-batch-make-parser -o OUT IN.by
    emacs -l semantic/wisent/grammar -f wisent-batch-make-parser -o OUT IN.wy

The outputs land beside their consumers in lisp/cedet/ (and are
.gitignore'd, like loaddefs.el).  Without them ~20 cedet files fail to
byte-compile with "Cannot open load file".  Run before compile-main so
list_lisp_files.py picks the generated .el into the manifest.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# (source under admin/grammars/, output .el under lisp/cedet/, kind).
# grammar.wy is generated first: it produces semantic/grammar-wy.el, the
# parser for the grammar language itself.  semantic/grammar.el loads it
# (falling back to the committed semantic/grm-wy-boot.el when absent), so
# the remaining wisent grammars can be built either way.
GRAMMARS = [
    ("grammar.wy",           "semantic/grammar-wy.el",        "wisent"),
    ("c.by",                 "semantic/bovine/c-by.el",       "bovine"),
    ("make.by",              "semantic/bovine/make-by.el",    "bovine"),
    ("scheme.by",            "semantic/bovine/scm-by.el",     "bovine"),
    ("java-tags.wy",         "semantic/wisent/javat-wy.el",   "wisent"),
    ("js.wy",                "semantic/wisent/js-wy.el",      "wisent"),
    ("python.wy",            "semantic/wisent/python-wy.el",  "wisent"),
    ("srecode-template.wy",  "srecode/srt-wy.el",             "wisent"),
]


# Recursive EMACSLOADPATH over lisp/, mirroring byte_compile_batch.py:
# emacs-lisp first (for the core 'debug feature etc.), obsolete and the
# nested cedet/* directories dropped (cedet sub-packages resolve via the
# cedet entry through their slash-prefixed features).  Must include
# lisp/international so semantic can load mule-util.
def _load_path(lisp_root: Path) -> list[str]:
    paths = [str(lisp_root), str(lisp_root / "emacs-lisp")]
    skip = {"emacs-lisp", "obsolete"}
    for d in sorted(lisp_root.rglob("*")):
        if not d.is_dir():
            continue
        rel = d.relative_to(lisp_root).as_posix()
        if rel in skip or any(rel.startswith(s + "/") for s in skip):
            continue
        if rel.startswith("cedet/"):
            continue
        paths.append(str(d))
    return paths


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-emacs", required=True)
    p.add_argument("--dump-file", type=Path,
                   help="bootstrap-emacs.pdmp; run as the dumped emacs.")
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--stamp", required=True, type=Path)
    args = p.parse_args()

    src_root = args.source_root.resolve()
    lisp = src_root / "lisp"
    grammars_dir = src_root / "admin" / "grammars"
    cedet = lisp / "cedet"

    env = os.environ.copy()
    env["EMACSDATA"] = str(src_root / "etc")
    env["EMACSDOC"] = str(src_root / "etc")
    env["EMACSLOADPATH"] = ":".join(_load_path(lisp))

    for source, output, kind in GRAMMARS:
        infile = grammars_dir / source
        outfile = cedet / output
        outfile.parent.mkdir(parents=True, exist_ok=True)
        loader, func = {
            "bovine": ("semantic/bovine/grammar", "bovine-batch-make-parser"),
            "wisent": ("semantic/wisent/grammar", "wisent-batch-make-parser"),
        }[kind]
        cmd = [args.bootstrap_emacs]
        if args.dump_file is not None:
            cmd.append(f"--dump-file={args.dump_file}")
        cmd += [
            "--batch", "--no-site-file", "--no-site-lisp",
            "--eval", "(setq load-prefer-newer t)",
            # The pbootstrap image lacks the cl-extra autoloads (see
            # byte_compile_batch.py); semantic's macros need them.
            "--eval", "(load \"cl-loaddefs\" 'noerror 'quiet)",
            "-l", loader,
            "-f", func,
            "-o", str(outfile), str(infile),
        ]
        print(f"generating {output} from admin/grammars/{source}",
              file=sys.stderr, flush=True)
        rc = subprocess.run(cmd, env=env).returncode
        if rc != 0 or not outfile.exists():
            print(f"  FAILED to generate {output}", file=sys.stderr)
            return rc or 1

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
