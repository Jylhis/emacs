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

  # --- Core + native-lisp split (caching) ------------------------------------
  # Fast "core": AOT-compiles only the preloaded lisp; the rest JITs at runtime
  # unless the companion native-lisp package is co-installed.  A C change
  # rebuilds only this; the eln tree below is untouched.
  emacs-jylhis-core = final.callPackage ./package.nix {
    root = src;
    nativeFullAot = false;
  };

  # The remaining lisp/ tree, AOT-compiled against emacs-jylhis-core as a
  # separate, independently-cached derivation.  Co-install with the core
  # (same profile) for full AOT coverage without a JIT first-run cost.
  emacs-jylhis-native-lisp = final.callPackage ./native-lisp.nix {
    emacs-core = final.emacs-jylhis-core;
  };

  # Shorthand package set for the default build.
  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
