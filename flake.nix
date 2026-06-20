{
  description = "GNU Emacs (Jylhis fork) packaged with Nix, built from this checkout";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    emacs-overlay = {
      url = "github:nix-community/emacs-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      emacs-overlay,
      treefmt-nix,
    }:
    let
      inherit (nixpkgs) lib;
      overlay = import ./nix/overlay.nix { src = ./.; };
    in
    {
      overlays.default = overlay;
      lib = import ./nix/lib.nix { inherit emacs-overlay; };

      nixosModules.default = ./nix/modules/nixos.nix;
      homeManagerModules.default = ./nix/modules/home-manager.nix;
      darwinModules.default = ./nix/modules/darwin.nix;
    }
    // flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            emacs-overlay.overlays.default
            overlay
          ];
        };
        treefmtEval = treefmt-nix.lib.evalModule pkgs ./nix/treefmt.nix;
      in
      {
        packages =
          {
            default = pkgs.emacs-jylhis;
            emacs = pkgs.emacs-jylhis;
            emacs-nox = pkgs.emacs-jylhis-nox;
            # Core + native-lisp split (independently cached); co-install both.
            emacs-core = pkgs.emacs-jylhis-core;
            emacs-native-lisp = pkgs.emacs-jylhis-native-lisp;
          }
          // lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
            emacs-pgtk = pkgs.emacs-jylhis-pgtk;
            emacs-gtk3 = pkgs.emacs-jylhis-gtk3;
          }
          // lib.optionalAttrs pkgs.stdenv.hostPlatform.isDarwin {
            emacs-macos = pkgs.emacs-jylhis-macos;
          };

        devShells.default = import ./nix/devshell.nix {
          inherit pkgs lib;
          emacs-jylhis = pkgs.emacs-jylhis;
        };

        formatter = treefmtEval.config.build.wrapper;

        checks.formatting = treefmtEval.config.build.check self;
      }
    );
}
