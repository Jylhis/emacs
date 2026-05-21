{ lib, pkgs, ... }:

{
  options.programs.emacs-jylhis = {
    enable = lib.mkEnableOption "the Jotain (Jylhis fork) GNU Emacs build";

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
        from this flake's overlay.  Substitute one of the variants
        (`emacs-jylhis-pgtk`, `emacs-jylhis-nox`, `emacs-jylhis-gtk3`) to
        change toolkit or strip the GUI.
      '';
    };

    defaultEditor = lib.mkEnableOption ''
      setting `EDITOR=emacsclient` (NixOS / Darwin) or
      `home.sessionVariables.EDITOR` (home-manager).
    '';

    extraPackages = lib.mkOption {
      type = lib.types.functionTo (lib.types.listOf lib.types.package);
      default = _epkgs: [ ];
      defaultText = lib.literalExpression "epkgs: []";
      description = ''
        Function returning a list of additional Emacs Lisp packages to
        install (taken from `pkgs.emacsPackagesFor cfg.package`).
      '';
    };
  };
}
