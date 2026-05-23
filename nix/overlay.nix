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

  # Host build whose $out/share/emacs/host-build/ supplies
  # bootstrap-emacs + emacs.pdmp + the byte-compiled lisp tree to
  # the Android cross-compile.
  emacs-jylhis-host-for-android = final.callPackage ./package.nix {
    inherit src;
    noGui = true;
    exposeHostBuild = true;
  };

  emacs-jylhis-android =
    if final.stdenv.hostPlatform.isLinux then
      final.callPackage ./android.nix {
        inherit src;
        emacsHost = final.emacs-jylhis-host-for-android;
        androidComposition = final.androidenv.composeAndroidPackages {
          platformVersions = [ "35" ];
          buildToolsVersions = [ "35.0.0" ];
          includeNDK = true;
          ndkVersions = [ "27.0.12077973" ];
          abiVersions = [ "arm64-v8a" ];
        };
      }
    else
      null;

  emacsPackagesFor-jylhis = final.emacsPackagesFor final.emacs-jylhis;
}
