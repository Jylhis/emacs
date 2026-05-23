{
  description = "Jotain Emacs -- GNU Emacs 31 from the Jylhis fork (Meson build)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    emacs-overlay = {
      url = "github:nix-community/emacs-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      treefmt-nix,
      emacs-overlay,
    }:
    let
      modules = import ./nix/modules;

      src = import ./nix/src-filter.nix {
        lib = nixpkgs.lib;
        root = ./.;
      };

      overlay = import ./nix/overlay.nix { inherit src; };
    in
    {
      overlays.default = overlay;

      nixosModules.default = modules.nixos;
      darwinModules.default = modules.darwin;
      homeManagerModules.default = modules.home-manager;

      lib = import ./nix/lib.nix { inherit emacs-overlay; };
    }
    // flake-utils.lib.eachSystem [
      "x86_64-linux"
      "aarch64-linux"
      "x86_64-darwin"
      "aarch64-darwin"
    ] (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
          # The Android SDK ships a non-free license; opt into it
          # only via this flake's androidenv consumer.
          config.android_sdk.accept_license = true;
          config.allowUnfree = true;
        };

        treefmtEval = treefmt-nix.lib.evalModule pkgs ./nix/treefmt.nix;

        isLinux = pkgs.stdenv.hostPlatform.isLinux;
      in
      {
        packages = {
          default = pkgs.emacs-jylhis;
          emacs = pkgs.emacs-jylhis;
          emacs-nox = pkgs.emacs-jylhis-nox;
          emacs-pgtk = pkgs.emacs-jylhis-pgtk;
          emacs-gtk3 = pkgs.emacs-jylhis-gtk3;
          emacs-debug = pkgs.emacs-jylhis-debug;
        }
        // pkgs.lib.optionalAttrs isLinux {
          emacs-android = pkgs.emacs-jylhis-android;
        };

        apps.default = {
          type = "app";
          program = "${pkgs.emacs-jylhis}/bin/emacs";
        };

        legacyPackages = pkgs;

        formatter = treefmtEval.config.build.wrapper;

        devShells = pkgs.lib.optionalAttrs isLinux {
          # Interactive shell for hacking on the Android port.  Has
          # the SDK + NDK + JDK + meson/ninja/python in $PATH; you
          # drive the build with `meson setup build-android ...`
          # directly.  See cross/meson-android.cross for invocation.
          android =
            let
              androidComposition = pkgs.androidenv.composeAndroidPackages {
                platformVersions = [ "35" ];
                buildToolsVersions = [ "35.0.0" ];
                includeNDK = true;
                ndkVersions = [ "27.0.12077973" ];
                abiVersions = [ "arm64-v8a" ];
              };
              androidSdk = "${androidComposition.androidsdk}/libexec/android-sdk";
            in
            pkgs.mkShell {
              name = "emacs-android";
              nativeBuildInputs = [
                pkgs.meson
                pkgs.ninja
                pkgs.pkg-config
                pkgs.python3
                pkgs.m4
                pkgs.jdk17_headless
                androidComposition.androidsdk
              ];
              shellHook = ''
                export ANDROID_HOME=${androidSdk}
                export ANDROID_SDK_ROOT=${androidSdk}
                export ANDROID_NDK_ROOT=${androidSdk}/ndk-bundle
                export PATH=${androidSdk}/ndk-bundle/toolchains/llvm/prebuilt/linux-x86_64/bin:$PATH
                echo "emacs-android dev shell -- aarch64-linux-android cross."
                echo "  ANDROID_HOME=$ANDROID_HOME"
                echo "  ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT"
                echo
                echo "  meson setup build && meson compile -C build"
                echo "  meson setup build-android \\"
                echo "    --cross-file cross/meson-android.cross \\"
                echo "    -Dandroid=enabled \\"
                echo "    -Dandroid-ndk=\$ANDROID_NDK_ROOT \\"
                echo "    -Dandroid-sdk=\$ANDROID_HOME \\"
                echo "    -Dandroid-host-build=\$PWD/build"
                echo "  meson compile -C build-android apk"
              '';
            };
        };

        checks = {
          emacs-nox = pkgs.emacs-jylhis-nox;
          formatting = treefmtEval.config.build.check self;
        };
      }
    );
}
