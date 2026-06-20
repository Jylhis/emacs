# Overlay exposing the local Emacs build and its variants.  `src` is the
# repository root, threaded in from flake.nix so package.nix can filter it.
{ src }:

final: _prev: {
  # Default build: pgtk + native-comp on Linux, NS/Cocoa on Darwin.
  emacs-jylhis = final.callPackage ./package.nix { root = src; };

  # Terminal-only.
  emacs-jylhis-nox = final.callPackage ./package.nix {
    root = src;
    noGui = true;
  };

  # Explicit pure-GTK (Wayland-native) build.  withGTK3/withX defaults in
  # package.nix follow from withPgtk to satisfy nixpkgs' assertions.
  emacs-jylhis-pgtk = final.callPackage ./package.nix {
    root = src;
    withPgtk = true;
  };

  # Traditional GTK3/X11 build.
  emacs-jylhis-gtk3 = final.callPackage ./package.nix {
    root = src;
    withPgtk = false;
    withGTK3 = true;
  };

  # macOS Cocoa build.
  emacs-jylhis-macos = final.callPackage ./package.nix {
    root = src;
    withNS = true;
  };

  # Lighter build: native-compilation in *default* mode (NATIVE_FULL_AOT
  # dropped), so the ~1300 rarely-loaded libraries are left to runtime JIT
  # (cached in the user's eln-cache) instead of being AOT-compiled at build
  # time.  Faster to build and smaller closure than the full-AOT default,
  # at the cost of a one-off JIT compile the first time a deferred library is
  # used.  See nix/README.md for why this is NOT an incremental-caching split.
  emacs-jylhis-core = final.callPackage ./package.nix {
    root = src;
    nativeFullAot = false;
  };

  # Standalone helper programs (emacsclient, etags, …) — independent of the
  # Emacs C core, so they neither pull in temacs nor rebuild on src/*.c edits.
  emacs-jylhis-lib-src = final.callPackage ./lib-src.nix { root = src; };

  # Shorthand package set for the default build.
  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
