#!/usr/bin/env bash
# admin/build-darwin-universal.sh -- merge two per-arch Emacs.app
# bundles into one universal bundle.
#
# Usage:
#   admin/build-darwin-universal.sh <amd64-app> <arm64-app> <out-app>
#
# Algorithm:
#   1. Copy arm64 bundle to <out-app> as a template.
#   2. For every regular file under <out-app>, check whether the
#      corresponding amd64 file is Mach-O.  If so, lipo-create the
#      universal version in-place.
#   3. Preserve native-comp .eln directories side-by-side -- they are
#      arch-specific (the trailing hash in
#      Contents/Resources/native-lisp/<emacs-ver>-<hash>/ differs per
#      arch), and Emacs picks the right one at runtime via
#      comp-eln-load-path.  We copy in any eln-tree from the amd64
#      bundle that doesn't already exist in the template.
#   4. Verify <out-app>/Contents/MacOS/Emacs shows both architectures.

set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <amd64-app> <arm64-app> <out-app>" >&2
  exit 2
fi

amd64=$1
arm64=$2
out=$3

for d in "$amd64" "$arm64"; do
  [ -d "$d" ] || { echo "missing bundle: $d" >&2; exit 1; }
  [ -x "$d/Contents/MacOS/Emacs" ] || {
    echo "no Mach-O at $d/Contents/MacOS/Emacs" >&2; exit 1; }
done

rm -rf "$out"
# -R preserves symlinks; -p preserves perms/times.
cp -Rp "$arm64/" "$out/"

# --- Step 2: lipo every Mach-O file in the template ----------------
lipo_count=0
copy_count=0
while IFS= read -r -d '' f; do
  rel=${f#"$out/"}
  amd_path="$amd64/$rel"
  # Skip symlinks (cp -R already preserved them).
  if [ -L "$f" ]; then continue; fi
  # Only consider regular files.
  if [ ! -f "$f" ]; then continue; fi
  # `file -b` reports e.g. "Mach-O 64-bit executable arm64" or
  # "Mach-O 64-bit dynamically linked shared library arm64".
  kind=$(file -b "$f" || true)
  case "$kind" in
    *Mach-O*|*"Mach-O universal"*)
      if [ -f "$amd_path" ]; then
        # In-place lipo: write to a temp then mv into place.
        tmp="${f}.uni"
        lipo -create "$amd_path" "$f" -output "$tmp"
        mv "$tmp" "$f"
        lipo_count=$((lipo_count + 1))
      else
        echo "warn: no amd64 counterpart for $rel (keeping arm64-only)" >&2
      fi
      ;;
  esac
done < <(find "$out" -type f -print0)

# --- Step 3: pull in arch-only files (mainly native-comp eln) -----
# Iterate over the amd64 tree; if a path is missing from the output,
# copy it in.  This is how the second arch's eln-cache directory lands
# in the universal bundle without overwriting the arm64 one.
while IFS= read -r -d '' f; do
  rel=${f#"$amd64/"}
  dst="$out/$rel"
  if [ -e "$dst" ] || [ -L "$dst" ]; then continue; fi
  mkdir -p "$(dirname "$dst")"
  cp -Rp "$f" "$dst"
  copy_count=$((copy_count + 1))
done < <(find "$amd64" \( -type f -o -type l \) -print0)

# --- Step 4: verify ------------------------------------------------
echo "lipo'd $lipo_count file(s); copied $copy_count amd64-only file(s)"
echo "--- lipo -info $out/Contents/MacOS/Emacs ---"
lipo -info "$out/Contents/MacOS/Emacs"

# Sanity: confirm both eln-cache dirs survived (if either was present).
if [ -d "$out/Contents/Resources/native-lisp" ]; then
  echo "--- native-lisp subdirs ---"
  ls -1 "$out/Contents/Resources/native-lisp"
fi
