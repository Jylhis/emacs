# Package this Emacs checkout by reusing the nixpkgs Emacs generic builder
# (Autotools-based) via override/overrideAttrs.  The builder already wires up
# native-comp eln load paths, site-start.el and the program wrapper; we only
# repoint it at the local source and run autogen.sh (a git tree ships no
# ./configure).
{
  lib,
  stdenv,
  emacs30,
  autoconf,
  automake,
  texinfo,
  root,
  # Variant toggles, mapped onto the nixpkgs override parameters.  The
  # overlay passes explicit combinations; the defaults below give a sensible
  # GUI build per platform (pgtk on Linux, NS/Cocoa on Darwin).
  #
  # nixpkgs' make-emacs asserts: pgtk requires the GTK3 codepath without X
  # (withPgtk -> withGTK3 && !withX) and NS is Darwin-only without X.
  noGui ? false,
  withPgtk ? stdenv.hostPlatform.isLinux && !noGui,
  withGTK3 ? withPgtk, # pgtk is built atop the GTK3 backend
  withX ? stdenv.hostPlatform.isLinux && !noGui && withGTK3 && !withPgtk,
  withNS ? stdenv.hostPlatform.isDarwin && !noGui,
  withNativeCompilation ? true,
  withTreeSitter ? true,
  # Full ahead-of-time native compilation of the whole lisp/ tree at build
  # time (nixpkgs default).  Set false for a fast "core" build that AOT-compiles
  # only the preloaded files and leaves the rest to runtime JIT — the basis of
  # the core + native-lisp derivation split (see nix/native-lisp.nix).
  nativeFullAot ? withNativeCompilation,
}:

let
  src = import ./src-filter.nix { inherit lib root; };
  version = "32.0.50";
  # The cheap "core": native-compile only the mandatory preloaded lisp; the
  # rest is supplied by the separate native-lisp derivation or JIT at runtime.
  preloadedElnOnly = withNativeCompilation && !nativeFullAot;
in
(emacs30.override {
  inherit
    noGui
    withPgtk
    withGTK3
    withX
    withNS
    withNativeCompilation
    withTreeSitter
    ;
  withSQLite3 = true;
  withWebP = true;
}).overrideAttrs
  (old: {
    pname =
      "emacs-jylhis" + lib.optionalString noGui "-nox" + lib.optionalString preloadedElnOnly "-core";
    inherit version src;

    # Drop NATIVE_FULL_AOT for the core build so `make` only AOT-compiles the
    # preloaded lisp; everything else is left for runtime JIT.  Keep the rest
    # of nixpkgs' env (notably LIBRARY_PATH for the native-comp driver).
    env =
      if preloadedElnOnly then removeAttrs (old.env or { }) [ "NATIVE_FULL_AOT" ] else (old.env or { });

    # Suppress async-JIT byproduct .eln during the lisp build: while
    # byte-compiling, Emacs would otherwise native-compile every dependency it
    # loads into the build's eln-cache (~1500 files) and install them.  With
    # JIT disabled, only the explicit preloaded .eln are produced, so the core
    # stays small and the rest is the native-lisp derivation's job.
    makeFlags =
      (old.makeFlags or [ ])
      ++ lib.optionals preloadedElnOnly [
        "BYTE_COMPILE_EXTRA_FLAGS=--eval '(setq native-comp-jit-compilation nil)'"
      ];

    # Drop the release-tarball-specific patches and postPatch from nixpkgs:
    # they target a pinned upstream version and do not apply to master.
    patches = [ ];
    postPatch = "";

    # A git checkout has no generated ./configure; regenerate it with the
    # upstream bootstrap script.  cleanSource has stripped .git, so autogen.sh
    # skips its git-hook setup and only runs autoreconf.
    nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
      autoconf
      automake
      texinfo
    ];
    preConfigure = ''
      ./autogen.sh
    ''
    + (old.preConfigure or "");

    # Guarantee the core ships only the preloaded .eln even if some JIT slipped
    # through: keep <abi>/preloaded/ and drop the top-level <abi>/*.eln.
    postInstall =
      (old.postInstall or "")
      + lib.optionalString preloadedElnOnly ''
        for abidir in "$out"/lib/emacs/${version}/native-lisp/*/; do
          [ -d "$abidir" ] || continue
          find "$abidir" -maxdepth 1 -name '*.eln' -delete
        done
      '';

    meta = (old.meta or { }) // {
      description = "GNU Emacs (Jylhis fork, built from local checkout)";
      mainProgram = "emacs";
    };
  })
