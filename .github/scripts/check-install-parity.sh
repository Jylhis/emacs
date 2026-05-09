#!/usr/bin/env bash
# Verify that a staged Meson install (DESTDIR) contains the same set
# of artefacts that the autotools install used to produce.  Regresses
# any build_by_default flip or install-step omission.
#
# Usage: check-install-parity.sh PREFIX VERSION ARCH
#   PREFIX  -- the staged prefix (e.g. /tmp/stage/usr/local)
#   VERSION -- emacs version (e.g. 31.0.50)
#   ARCH    -- system_configuration (e.g. x86_64-linux, x86_64-darwin)
#
# Reference: src/Makefile.in install-arch-{dep,indep} and
# lisp/Makefile.in install-arch-indep at anchor 08a22b8965ec.
set -euo pipefail

if [ $# -ne 3 ]; then
  echo "usage: $0 PREFIX VERSION ARCH" >&2
  exit 2
fi
prefix=$1
version=$2
arch=$3

bindir=$prefix/bin
datadir=$prefix/share/emacs/$version
libexecdir=$prefix/libexec/emacs/$version/$arch

# Required: must exist or the build is incomplete.
required=(
  "$bindir/emacs"
  "$bindir/emacs-$version"
  "$bindir/emacsclient"
  "$libexecdir/emacs.pdmp"
  "$libexecdir/etc/DOC"
  "$datadir/lisp/loaddefs.elc"
  "$datadir/lisp/dired.elc"
  "$datadir/lisp/dired-loaddefs.elc"
  "$datadir/lisp/international/charprop.el"
  "$datadir/lisp/international/uni-name.el"
  "$datadir/lisp/international/charscript.elc"
  "$datadir/lisp/international/emoji-zwj.elc"
  "$datadir/lisp/subdirs.el"
  "$datadir/etc/tutorials/TUTORIAL"
  "$datadir/lisp/leim/leim-list.elc"
  "$datadir/lisp/leim/quail/CCDOSPY.elc"
  "$datadir/lisp/leim/ja-dic/ja-dic.elc"
  "$datadir/lisp/language/pinyin.elc"
)

# Required compressed-or-not: pre-compress and uncompressed both pass.
# (Mirrors compress-install=true vs false.)
required_either=(
  "$datadir/lisp/loaddefs.el"
  "$datadir/lisp/dired-loaddefs.el"
  "$datadir/lisp/international/charscript.el"
  "$datadir/lisp/international/emoji-zwj.el"
)

missing=0
for path in "${required[@]}"; do
  if [ ! -e "$path" ]; then
    echo "MISSING: $path"
    missing=$((missing + 1))
  fi
done

for path in "${required_either[@]}"; do
  if [ ! -e "$path" ] && [ ! -e "$path.gz" ]; then
    echo "MISSING: $path (or $path.gz)"
    missing=$((missing + 1))
  fi
done

# Sanity counts: the byte-compiled tree should have several hundred
# .elc files, not just one or two.  Catches a regression where the
# install-time .elc walk skips a directory.
elc_count=$(find "$datadir/lisp" -name '*.elc' 2>/dev/null | wc -l)
if [ "$elc_count" -lt 1000 ]; then
  echo "TOO FEW elc: only $elc_count under $datadir/lisp (expected >= 1000)"
  missing=$((missing + 1))
fi

if [ "$missing" -gt 0 ]; then
  echo
  echo "Install parity check FAILED ($missing missing/anomalous entries)"
  exit 1
fi

echo "Install parity check PASSED ($elc_count .elc files installed)"
