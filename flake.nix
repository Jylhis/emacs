{
  description = "Jotain Emacs -- GNU Emacs 31 from the Jylhis fork (Meson build)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/a0991c886dc83e6e9de01d5266e4842985b1850e";
    flake-utils.url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";

    treefmt-nix = {
      url = "github:numtide/treefmt-nix/790751ff7fd3801feeaf96d7dc416a8d581265ba";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    emacs-overlay = {
      url = "github:nix-community/emacs-overlay/7f69e608e6ac16770c3bcd28acb188adcf1b67a2";
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

      overlay = import ./nix/overlay.nix {
        inherit src;
        externalPackagesModule = import ./nix/external-packages.nix;
        externalSourcesModule  = import ./nix/external-sources.nix;
      };
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
        };

        treefmtEval = treefmt-nix.lib.evalModule pkgs ./nix/treefmt.nix;
      in
      {
        packages = {
          default = pkgs.emacs-jylhis;
          emacs = pkgs.emacs-jylhis;
          emacs-nox = pkgs.emacs-jylhis-nox;
          emacs-pgtk = pkgs.emacs-jylhis-pgtk;
          emacs-gtk3 = pkgs.emacs-jylhis-gtk3;
          emacs-debug = pkgs.emacs-jylhis-debug;
          external-sources = pkgs.emacs-external-sources;
        };

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
