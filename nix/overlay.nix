{ src }:

final: _prev: {
  emacs-jylhis = final.callPackage ./package.nix { inherit src; };

  emacs-jylhis-nox = final.callPackage ./package.nix {
    inherit src;
    noGui = true;
  };

  emacs-jylhis-pgtk = final.callPackage ./package.nix {
    inherit src;
    withPgtk = true;
    withGTK3 = false;
  };

  emacs-jylhis-gtk3 = final.callPackage ./package.nix {
    inherit src;
    withGTK3 = true;
    withPgtk = false;
  };

  emacs-jylhis-macos = final.callPackage ./package.nix {
    inherit src;
    withNS = true;
    withNsSelfContained = true;
    withSystemAppearancePatch = true;
    withRoundUndecoratedPatch = true;
    withFixNsXColorsPatch = true;
  };

  emacs-jylhis-debug = final.callPackage ./package.nix {
    inherit src;
    extraMesonFlags = [
      "-Dbuildtype=debug"
      "-Dcheck=yes,glyphs"
      "-Dcheck-lisp-object-type=true"
    ];
  };

  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
