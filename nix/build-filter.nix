# Source filter for the split build derivations.  Drops the content that
# churns during development — the Lisp tree (*.el) and the Emacs C core
# (src/*.c, src/*.m) — while keeping everything `configure`/`autoreconf` needs,
# notably the gnulib sources under lib/ (autoreconf's AC_LIBSOURCES requires
# them) and every build-system file (*.in, m4/, configure.ac).
#
# A derivation built from this source therefore does NOT rebuild when a
# src/*.c or a lisp/*.el file is edited — the basis of the lib-src / skeleton
# split.
{ lib, root }:

let
  rootStr = toString root;
in
lib.cleanSourceWith {
  src = root;
  name = "emacs-jylhis-build-src";
  filter =
    path: _type:
    let
      base = baseNameOf (toString path);
      rel = lib.removePrefix (rootStr + "/") (toString path);
      inSrc = lib.hasPrefix "src/" rel;
    in
    !(builtins.elem base [
      ".git"
      ".direnv"
      ".devenv"
      ".envrc"
      ".envrc.local"
      "build"
      "flake.nix"
      "flake.lock"
      "default.nix"
      ".claude"
      "nix"
      "result"
    ])
    && !(lib.hasPrefix "result" base)
    && !(lib.hasSuffix ".lock" base)
    # Churning content — dropped so edits to it don't invalidate the build.
    && !(lib.hasSuffix ".el" base)
    && !(lib.hasSuffix ".elc" base)
    && !(lib.hasSuffix ".eln" base)
    && !(lib.hasSuffix ".pdmp" base)
    && !(inSrc && lib.hasSuffix ".c" base)
    && !(inSrc && lib.hasSuffix ".m" base);
}
