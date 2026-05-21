{
  lib,
  pkgs,
  config,
  ...
}:

let
  cfg = config.programs.emacs-jylhis;
  emacsPkg = (pkgs.emacsPackagesFor cfg.package).emacsWithPackages cfg.extraPackages;
in
{
  imports = [ ./program.nix ];

  config = lib.mkIf cfg.enable {
    home.packages = [ emacsPkg ];

    home.sessionVariables = lib.mkIf cfg.defaultEditor {
      EDITOR = "emacsclient";
    };
  };
}
