# Shared options for the Jylhis Emacs build, imported by the NixOS,
# home-manager and nix-darwin modules.  Defines the option surface and the
# computed `finalPackage` (Emacs + requested Elisp packages); each platform
# module consumes `finalPackage` to install it and, optionally, run the daemon.
{
  lib,
  pkgs,
  config,
  ...
}:

let
  cfg = config.programs.emacs-jylhis;
in
{
  options.programs.emacs-jylhis = {
    enable = lib.mkEnableOption "the Jylhis fork GNU Emacs build";

    package = lib.mkOption {
      type = lib.types.package;
      default =
        pkgs.emacs-jylhis or (throw ''
          programs.emacs-jylhis.package: the Emacs derivation is not in pkgs.
          Apply the flake's overlay first:
              nixpkgs.overlays = [ inputs.emacs-jylhis.overlays.default ];
        '');
      defaultText = lib.literalExpression "pkgs.emacs-jylhis";
      description = ''
        Which Emacs derivation to install.  Defaults to `pkgs.emacs-jylhis`
        from this flake's overlay.  Substitute a variant
        (`emacs-jylhis-pgtk`, `emacs-jylhis-nox`, `emacs-jylhis-gtk3`,
        `emacs-jylhis-macos`) to change toolkit or strip the GUI.
      '';
    };

    extraPackages = lib.mkOption {
      type = lib.types.functionTo (lib.types.listOf lib.types.package);
      default = _epkgs: [ ];
      defaultText = lib.literalExpression "epkgs: [ ]";
      description = ''
        Function returning extra Emacs Lisp packages to install, taken from
        `pkgs.emacsPackagesFor cfg.package`.
      '';
    };

    extraProfilePackages = lib.mkOption {
      type = lib.types.listOf lib.types.package;
      default = [ ];
      example = lib.literalExpression "[ pkgs.ripgrep pkgs.fd ]";
      description = ''
        Extra packages installed into the same profile/system as Emacs — for
        tools the daemon should find on PATH (ripgrep, language servers, etc.).
      '';
    };

    finalPackage = lib.mkOption {
      type = lib.types.package;
      readOnly = true;
      description = ''
        The Emacs package actually installed: `package` wrapped with
        `extraPackages`.  Read-only; consumed by the daemon service.
      '';
    };

    defaultEditor = lib.mkEnableOption ''
      setting `EDITOR=emacsclient` (NixOS / nix-darwin) or
      `home.sessionVariables.EDITOR` (home-manager)
    '';

    daemon = {
      enable = lib.mkEnableOption ''
        a per-user Emacs daemon (`emacs --fg-daemon`) as a systemd user
        service (Linux) or launchd user agent (macOS).  Connect with
        `emacsclient`
      '';

      extraOptions = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        default = [ ];
        example = [ "--debug-init" ];
        description = "Extra command-line arguments passed to the daemon.";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    programs.emacs-jylhis.finalPackage =
      (pkgs.emacsPackagesFor cfg.package).emacsWithPackages cfg.extraPackages;
  };
}
