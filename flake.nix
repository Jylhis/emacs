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
        packages = {
          default = pkgs.emacs-jylhis;
          emacs = pkgs.emacs-jylhis;
          emacs-nox = pkgs.emacs-jylhis-nox;
          # Lighter build: defers rarely-used libraries to runtime JIT.
          emacs-core = pkgs.emacs-jylhis-core;
          # Standalone helper programs (emacsclient, etags, …).
          emacs-tools = pkgs.emacs-jylhis-lib-src;
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
          inherit (pkgs) emacs-jylhis;
        };

        formatter = treefmtEval.config.build.wrapper;

        checks = {
          formatting = treefmtEval.config.build.check self;

          # Build the terminal Emacs and assert it runs, has native
          # compilation, and has tree-sitter linked in.
          emacs-smoke = pkgs.runCommand "emacs-jylhis-smoke" { } ''
            e=${pkgs.emacs-jylhis-nox}/bin/emacs
            test "$($e --batch --eval '(princ (+ 1 1))')" = 2
            $e --batch --eval '(unless (native-comp-available-p) (error "native-comp missing"))'
            $e --batch --eval '(unless (treesit-available-p) (error "tree-sitter missing"))'
            touch $out
          '';
        };
      }
    );
}
