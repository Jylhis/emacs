# nix-darwin module: install the Jylhis Emacs build and, optionally, run it as
# a per-user launchd agent (emacs --fg-daemon).  Mirrors nix-darwin's
# modules/services/emacs.nix.
{
  lib,
  config,
  ...
}:

let
  cfg = config.programs.emacs-jylhis;
in
{
  imports = [ ./program.nix ];

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [ cfg.finalPackage ] ++ cfg.extraProfilePackages;

    environment.variables = lib.mkIf cfg.defaultEditor {
      EDITOR = "emacsclient";
    };

    launchd.user.agents.emacs = lib.mkIf cfg.daemon.enable {
      serviceConfig = {
        ProgramArguments = [
          "${cfg.finalPackage}/bin/emacs"
          "--fg-daemon"
        ]
        ++ cfg.daemon.extraOptions;
        RunAtLoad = true;
        KeepAlive = true;
      };
    };
  };
}
