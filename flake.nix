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
        inherit (nixpkgs) lib;
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
    //
      flake-utils.lib.eachSystem
        [
          "x86_64-linux"
          "aarch64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ]
        (
          system:
          let
            pkgs = import nixpkgs {
              inherit system;
              overlays = [ self.overlays.default ];
            };

            treefmtEval = treefmt-nix.lib.evalModule pkgs ./nix/treefmt.nix;
          in
          {
            packages = {
              default = pkgs.emacs-jylhis;
              emacs = pkgs.emacs-jylhis;
              emacs-nox = pkgs.emacs-jylhis-nox;
              emacs-debug = pkgs.emacs-jylhis-debug;
            }
            // (
              if pkgs.stdenv.isDarwin then
                { emacs-macos = pkgs.emacs-jylhis-macos; }
              else
                {
                  emacs-pgtk = pkgs.emacs-jylhis-pgtk;
                  emacs-gtk3 = pkgs.emacs-jylhis-gtk3;
                }
            );

            apps.default = {
              type = "app";
              program = "${pkgs.emacs-jylhis}/bin/emacs";
            };

            legacyPackages = pkgs;

            formatter = treefmtEval.config.build.wrapper;

            checks = {
              emacs-nox = pkgs.emacs-jylhis-nox;
              formatting = treefmtEval.config.build.check self;
            };
          }
        );
}
