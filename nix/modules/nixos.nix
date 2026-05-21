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
    environment.systemPackages = [ emacsPkg ];

    environment.variables = lib.mkIf cfg.defaultEditor {
      EDITOR = lib.mkOverride 900 "emacsclient";
    };
  };
}
