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
  };

  emacs-jylhis-debug = final.callPackage ./package.nix {
    inherit src;
    extraConfigureFlags = [
      "--enable-checking=yes,glyphs"
      "--enable-check-lisp-object-type"
    ];
  };

  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
