{ src, externalPackagesModule, externalSourcesModule }:

final: _prev:
let
  externalPackages = externalPackagesModule { pkgs = final; };
  externalSources  = externalSourcesModule {
    pkgs = final;
    inherit externalPackages;
  };

  callEmacs = args:
    final.callPackage ./package.nix ({
      inherit src externalSources;
    } // args);
in
{
  emacs-external-sources = externalSources;

  emacs-jylhis        = callEmacs { };
  emacs-jylhis-nox    = callEmacs { noGui = true; };
  emacs-jylhis-pgtk   = callEmacs { withPgtk = true; withGTK3 = false; };
  emacs-jylhis-gtk3   = callEmacs { withGTK3 = true; withPgtk = false; };
  emacs-jylhis-debug  = callEmacs {
    extraMesonFlags = [
      "-Dbuildtype=debug"
      "-Dcheck=yes,glyphs"
      "-Dcheck-lisp-object-type=true"
    ];
  };

  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
