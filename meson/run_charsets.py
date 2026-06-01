#!/usr/bin/env python3
"""Generate etc/charsets/*.map files from admin/charsets/.

Replicates admin/charsets/Makefile.in's awk-pipeline rules without
requiring autotools' ./configure to have been run.  All rules expand
to one of a few patterns:

  - "GLIBC-1": run mapconv on a glibc charmap .gz with a regex,
              compact filter, GLIBC-1 format.  Used for ~80
              single-byte charsets.
  - "GLIBC-2", "GLIBC-2-7": double-byte glibc charmaps.
  - "UNICODE", "UNICODE2", "IANA", "CZYBORRA", "KANJI-DATABASE":
              non-glibc input formats.
  - "copy": just cp a hand-maintained mapfile.
  - special-cased: ALTERNATIVNYJ, BIG5-1/2, JISC6226, JISX2131,
              JISX2132, GB180304, CP932-2BYTE, cp51932.el,
              eucjp-ms.el, JISX0201, JISX0208.

See admin/charsets/Makefile.in:127-313 for the original rules and
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import subprocess
import sys
from pathlib import Path

# Single-byte charset names (8859-N, KA-*, EBCDIC*, plus simple ones).
# Each maps to (glibc_charmap_basename, regex).
SINGLE_BYTE_RULES = {
    # 8859-%.map -> ISO-8859-%.gz
    **{
        f"8859-{n}.map": (f"ISO-8859-{n}.gz", r'/^<.*[ \t]\/x/')
        for n in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
    },
    # EBCDIC%.map -> EBCDIC-%.gz
    **{
        f"EBCDIC{name}.map": (f"EBCDIC-{name}.gz", r'/^<.*[ \t]\/x/')
        for name in ["UK", "US"]
    },
    # KA-%.map -> GEORGIAN-%.gz
    **{
        f"KA-{lang}.map": (f"GEORGIAN-{lang}.gz", r'/^<.*[ \t]\/x/')
        for lang in ["PS", "ACADEMY"]
    },
    # IBM%.map -> IBM%.gz (general %.map fallback)
    **{
        f"IBM{n}.map": (f"IBM{n}.gz", r'/^<.*[ \t]\/x/')
        for n in [
            "037", "038", "256", "273", "274", "275", "277", "278",
            "280", "281", "284", "285", "290", "297", "420", "423",
            "424", "437", "500", "850", "851", "852", "855", "856",
            "857", "860", "861", "862", "863", "864", "865", "866",
            "868", "869", "870", "871", "874", "875", "880", "891",
            "903", "904", "905", "918", "1004", "1026", "1047",
        ]
    },
    # CP%.map -> CP%.gz
    **{
        f"CP{n}.map": (f"CP{n}.gz", r'/^<.*[ \t]\/x/')
        for n in [
            "737", "775", "1125", "1250", "1251", "1252", "1253",
            "1254", "1255", "1256", "1257", "1258", "10007",
        ]
    },
    # Other simple charsets.
    "KOI-8.map":     ("KOI-8.gz", r'/^<.*[ \t]\/x/'),
    "KOI8-R.map":    ("KOI8-R.gz", r'/^<.*[ \t]\/x/'),
    "KOI8-U.map":    ("KOI8-U.gz", r'/^<.*[ \t]\/x/'),
    "KOI8-T.map":    ("KOI8-T.gz", r'/^<.*[ \t]\/x/'),
    "TIS-620.map":   ("TIS-620.gz", r'/^<.*[ \t]\/x/'),
    "VISCII.map":    ("VISCII.gz", r'/^<.*[ \t]\/x/'),
    "HP-ROMAN8.map": ("HP-ROMAN8.gz", r'/^<.*[ \t]\/x/'),
    "NEXTSTEP.map":  ("NEXTSTEP.gz", r'/^<.*[ \t]\/x/'),
    "MACINTOSH.map": ("MACINTOSH.gz", r'/^<.*[ \t]\/x/'),
}

# Mapfiles copied from admin/charsets/mapfiles/ verbatim.
COPY_RULES = {
    "CP720.map":     "mapfiles/CP720.map",
    "CP858.map":     "mapfiles/CP858.map",
    "JISX213A.map":  "mapfiles/JISX213A.map",
    "MULE-ethiopic.map":   "mapfiles/MULE-ethiopic.map",
    "MULE-ipa.map":        "mapfiles/MULE-ipa.map",
    "MULE-is13194.map":    "mapfiles/MULE-is13194.map",
    "MULE-sisheng.map":    "mapfiles/MULE-sisheng.map",
    "MULE-tibetan.map":    "mapfiles/MULE-tibetan.map",
    "MULE-lviscii.map":    "mapfiles/MULE-lviscii.map",
    "MULE-uviscii.map":    "mapfiles/MULE-uviscii.map",
}

def run_mapconv(charsets_dir: Path, input_file: Path, regex: str,
                style: str, awk_script: Path | None,
                output: Path) -> None:
    """Invoke admin/charsets/mapconv (an awk wrapper) like
    `run_mapconv $< REGEX STYLE [SCRIPT] > $@`.

    Raises CalledProcessError if mapconv exits non-zero so the
    overall charsets target fails fast instead of writing a partial
    /empty .map file and leaving the stamp marker valid.
    """
    cmd = [str(charsets_dir / "mapconv"), str(input_file), regex, style]
    if awk_script is not None:
        cmd.append(str(awk_script))
    env = os.environ.copy()
    env["AWK"] = "awk"
    with output.open("w") as fp:
        subprocess.run(cmd, env=env, stdout=fp, check=True)

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--charsets-dir", required=True, type=Path,
                   help="path to admin/charsets/ in source tree")
    p.add_argument("--out-dir", required=True, type=Path,
                   help="path to etc/charsets/ output directory")
    p.add_argument("--lispint-dir", required=True, type=Path,
                   help="path to lisp/international/ for trans tables")
    p.add_argument("--stamp", required=True, type=Path,
                   help="touch this file when all charsets are written")
    args = p.parse_args()

    charsets_dir = args.charsets_dir.resolve()
    out_dir = args.out_dir.resolve()
    lispint_dir = args.lispint_dir.resolve()
    glibc = charsets_dir / "glibc"
    mapfiles = charsets_dir / "mapfiles"
    out_dir.mkdir(parents=True, exist_ok=True)

    compact = charsets_dir / "compact.awk"
    big5 = charsets_dir / "big5.awk"
    cp51932 = charsets_dir / "cp51932.awk"
    cp932 = charsets_dir / "cp932.awk"
    eucjp_ms = charsets_dir / "eucjp-ms.awk"
    gb180302 = charsets_dir / "gb180302.awk"
    gb180304 = charsets_dir / "gb180304.awk"
    kuten = charsets_dir / "kuten.awk"

    # Single-byte rules.  run_mapconv now raises on non-zero
    # mapconv exit (check=True), so we don't branch on a return code.
    for name, (glibc_name, regex) in SINGLE_BYTE_RULES.items():
        src = glibc / glibc_name
        if not src.exists():
            print(f"missing glibc charmap: {src}", file=sys.stderr)
            return 1
        run_mapconv(charsets_dir, src, regex, "GLIBC-1",
                    compact, out_dir / name)

    # Hand-copied mapfiles.
    import shutil
    for name, src in COPY_RULES.items():
        shutil.copy(charsets_dir / src, out_dir / name)

    # ----- Special rules. -----
    # VSCII (TCVN5712-1, GLIBC-1, custom regex).
    run_mapconv(charsets_dir, glibc / "TCVN5712-1.gz",
                r'/^<.*[ \t]\/x[0-9a-f].[ \t]/', "GLIBC-1",
                compact, out_dir / "VSCII.map")

    # VSCII-2: same but different regex + sed substitution.
    tmp = subprocess.run(
        [str(charsets_dir / "mapconv"), str(glibc / "TCVN5712-1.gz"),
         r'/^<.*[ \t]\/x[2-7a-f].[ \t]/', "GLIBC-1", str(compact)],
        env={**os.environ, "AWK": "awk"},
        capture_output=True, text=True,
    ).stdout
    tmp = re.sub(r"0x20-0x7F.*", "0x00-0x7F 0x0000", tmp)
    (out_dir / "VSCII-2.map").write_text(tmp)

    # ALTERNATIVNYJ.map: derived from IBM866.map via sed.
    ibm866 = (out_dir / "IBM866.map").read_text().splitlines()
    out = ["# Modified from IBM866.map according to the chart at",
           "# https://web.archive.org/web/20100131045151/"
           "http://www.cyrillic.com/ref/cyrillic/koi-8alt.html",
           "# with guesses for the Unicodes of the glyphs."]
    edits = {
        "0xF2": " 0x2019", "0xF3": " 0x2018", "0xF4": " 0x0301",
        "0xF5": " 0x0300", "0xF6": " 0x203A", "0xF7": " 0x2039",
        "0xF8": " 0x2191", "0xF9": " 0x2193", "0xFA": " 0x00B1",
        "0xFB": " 0x00F7",
    }
    for line in ibm866[1:]:
        for token, repl in edits.items():
            if line.lstrip().startswith(token) or token in line.split():
                line = re.sub(r"^(\S+).*", r"\1" + repl, line)
                break
        out.append(line)
    (out_dir / "ALTERNATIVNYJ.map").write_text("\n".join(out) + "\n")

    # MIK, PTCP154, stdenc, symbol -- non-glibc inputs.
    for name, (src, regex, fmt) in {
        "MIK.map":     ("bulgarian-mik.txt", r'1,$', "CZYBORRA"),
        "PTCP154.map": ("PTCP154", r'/^0x/', "IANA"),
        "stdenc.map":  ("stdenc.txt", r'/^[0-9A-Fa-f]/', "UNICODE"),
        "symbol.map":  ("symbol.txt", r'/^[0-9A-Fa-f]/', "UNICODE"),
    }.items():
        run_mapconv(charsets_dir, mapfiles / src, regex, fmt,
                    compact, out_dir / name)

    # Double-byte CJK charsets via mapconv GLIBC-2 / GLIBC-2-7.
    for name, (src, regex, fmt) in {
        "CP949-2BYTE.map": ("CP949.gz", r'/^<.*[ \t]\/x[89a-f]/', "GLIBC-2"),
        "GB2312.map":      ("GB2312.gz", r'/^<.*[ \t]\/x[a-f]/', "GLIBC-2-7"),
        "GBK.map":         ("GBK.gz", r'/^<.*[ \t]\/x[89a-f]/', "GLIBC-2"),
        "BIG5-HKSCS.map":  ("BIG5-HKSCS.gz", r'/^<.*[ \t]\/x[89a-f].\//', "GLIBC-2"),
        "JOHAB.map":       ("JOHAB.gz", r'/^<.*[ \t]\/x[89a-f]/', "GLIBC-2"),
        "KSC5601.map":     ("EUC-KR.gz", r'/^<.*[ \t]\/x[a-f]/', "GLIBC-2-7"),
        "JISX0212.map":    ("EUC-JP.gz", r'/^<.*[ \t]\/x8f/ s,/x8f,,', "GLIBC-2-7"),
        "JISX2132.map":    ("EUC-JISX0213.gz", r'/^<.*[ \t]\/x8f/ s,/x8f,,', "GLIBC-2-7"),
        "CNS-1.map":       ("EUC-TW.gz", r'/^<.*[ \t]\/x[a-f]/', "GLIBC-2-7"),
        "CNS-F.map":       ("EUC-TW.gz",
                            r'/^<.*\/x8e\/xaf/ s,/x8e/xaf,,', "GLIBC-2-7"),
    }.items():
        run_mapconv(charsets_dir, glibc / src, regex, fmt,
                    compact, out_dir / name)

    # BIG5: no compact pass.
    run_mapconv(charsets_dir, glibc / "BIG5.gz",
                r'/^<.*[ \t]\/x[a-f]/', "GLIBC-2", None,
                out_dir / "BIG5.map")

    # BIG5-1, BIG5-2 derived from BIG5.map via sed/big5.awk.  Mirrors
    # admin/charsets/Makefile.in:236-242:
    #   BIG5-1: sed -n '/0xa140/,/0xc8fe/p' < BIG5.map | awk -f big5.awk
    #   BIG5-2: sed -n '/0xc940/,$ p'       < BIG5.map | awk -f big5.awk
    big5_awk = charsets_dir / "big5.awk"
    big5_map_lines = (out_dir / "BIG5.map").read_text().splitlines(keepends=True)

    def sed_range(lines, start_pat, end_pat):
        out, on = [], False
        for line in lines:
            if not on and re.search(start_pat, line):
                on = True
            if on:
                out.append(line)
            if on and end_pat is not None and re.search(end_pat, line):
                on = False
        return "".join(out)

    for name, start, end in [("BIG5-1.map", r"0xa140", r"0xc8fe"),
                             ("BIG5-2.map", r"0xc940", None)]:
        sliced = sed_range(big5_map_lines, start, end)
        result = subprocess.run(
            ["awk", "-f", str(big5_awk)],
            input=sliced, capture_output=True, text=True,
        ).stdout
        (out_dir / name).write_text(
            f"# Generated from BIG5.map\n" + result)

    # KSC5636 follows the generic glibc rule (Makefile.in:303).
    run_mapconv(charsets_dir, glibc / "KSC5636.gz",
                r'/^<.*[ \t]\/x/', "GLIBC-1", compact,
                out_dir / "KSC5636.map")

    # GB180302, GB180304.
    run_mapconv(charsets_dir, glibc / "GB18030.gz",
                r'/^<.*[ \t]\/x..\/x..[ \t]/', "GLIBC-2",
                gb180302, out_dir / "GB180302.map")
    with (out_dir / "GB180304.map").open("w") as fp, \
         (out_dir / "GB180302.map").open("r") as stdin_fp:
        subprocess.run(
            ["awk", "-f", str(gb180304)],
            stdin=stdin_fp, stdout=fp,
        )

    # JISX0201.
    out = subprocess.run(
        [str(charsets_dir / "mapconv"), str(glibc / "JIS_X0201.gz"),
         r'/^<.*[ \t]\/x[0-9]/', "GLIBC-1", str(compact)],
        env={**os.environ, "AWK": "awk"},
        capture_output=True, text=True,
    ).stdout
    out += "# Generated by hand\n0xA1-0xDF 0xFF61\n"
    (out_dir / "JISX0201.map").write_text(out)

    # JISX0208.
    out = subprocess.run(
        [str(charsets_dir / "mapconv"), str(glibc / "EUC-JP.gz"),
         r'/^<.*[ \t]\/x[a-f]/', "GLIBC-2-7"],
        env={**os.environ, "AWK": "awk"},
        capture_output=True, text=True,
    ).stdout
    out = out.replace("0x2015", "0x2014")
    (out_dir / "JISX0208.map").write_text(out)

    # CP932-2BYTE.map.
    run_mapconv(charsets_dir, mapfiles / "CP932.TXT",
                r'/^0x[89A-F][0-9A-F][0-9A-F]/', "UNICODE2",
                cp932, out_dir / "CP932-2BYTE.map")

    # JISC6226.
    src = mapfiles / "Uni2JIS"
    base = subprocess.run(
        [str(charsets_dir / "mapconv"), str(src),
         r'/^[^#].*0-/', "YASUOKA", str(kuten)],
        env={**os.environ, "AWK": "awk"},
        capture_output=True, text=True,
    ).stdout
    base = re.sub(r"(0x2140.*)005C", r"\g<1>FF3C", base)
    base += ("0x3442 0x3D4E\n0x374E 0x25874\n"
             "0x3764 0x28EF6\n0x513D 0x2F80F\n0x7045 0x9724\n")
    (out_dir / "JISC6226.map").write_text(base)

    # CNS-2 through CNS-7 from cns2ucsdkw.txt.
    cns_src = mapfiles / "cns2ucsdkw.txt"
    for n in [2, 3, 4, 5, 6, 7]:
        run_mapconv(charsets_dir, cns_src, f'/^C{n}/', "KANJI-DATABASE",
                    compact, out_dir / f"CNS-{n}.map")

    # JISX2131.
    sed_script = out_dir.parent / ".jisx2131-filter"
    src_filter = (mapfiles / "JISX213A.map").read_text()
    lines = []
    for line in src_filter.splitlines():
        if line.startswith("#"):
            continue
        m = re.search(r".*0x([0-9A-Z]*)$", line)
        if m:
            lines.append(rf"/0x0*{m.group(1)}$/d")
    sed_script.write_text("\n".join(lines) + "\n")
    base = subprocess.run(
        [str(charsets_dir / "mapconv"), str(glibc / "EUC-JISX0213.gz"),
         r'/^<.*[ \t]\/x[a-f]/', "GLIBC-2-7"],
        env={**os.environ, "AWK": "awk"},
        capture_output=True, text=True,
    ).stdout
    base = subprocess.run(["sed", "-f", str(sed_script)],
                          input=base, capture_output=True, text=True).stdout
    base = base.replace("0x2015", "0x2014").replace("0x2299", "0x29BF")
    (out_dir / "JISX2131.map").write_text(base)

    # cp51932.el and eucjp-ms.el (in lisp/international/).
    lispint_dir.mkdir(parents=True, exist_ok=True)
    with (lispint_dir / "cp51932.el").open("w") as fp, \
         (out_dir / "CP932-2BYTE.map").open("r") as stdin_fp:
        subprocess.run(["awk", "-f", str(cp51932)],
                       stdin=stdin_fp, stdout=fp)
    with (lispint_dir / "eucjp-ms.el").open("w") as fp:
        gunz = subprocess.run(["gunzip", "-c", str(glibc / "EUC-JP-MS.gz")],
                              capture_output=True).stdout
        subprocess.run(["awk", "-f", str(eucjp_ms)],
                       input=gunz, stdout=fp)

    args.stamp.parent.mkdir(parents=True, exist_ok=True)
    args.stamp.write_text("ok\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
