{ src }:

final: _prev:
let
  externalSources = final.callPackage ./external-sources.nix { };
in
{
  emacs-jylhis = final.callPackage ./package.nix { inherit src externalSources; };

  emacs-jylhis-nox = final.callPackage ./package.nix {
    inherit src externalSources;
    noGui = true;
  };

  emacs-jylhis-pgtk = final.callPackage ./package.nix {
    inherit src externalSources;
    withPgtk = true;
    withGTK3 = false;
  };

  emacs-jylhis-gtk3 = final.callPackage ./package.nix {
    inherit src externalSources;
    withGTK3 = true;
    withPgtk = false;
  };

  emacs-jylhis-debug = final.callPackage ./package.nix {
    inherit src externalSources;
    extraMesonFlags = [
      "-Dbuildtype=debug"
      "-Dcheck=yes,glyphs"
      "-Dcheck-lisp-object-type=true"
    ];
  };

  emacs-jylhis-external-sources = externalSources;

  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
