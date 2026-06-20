# home-manager module: install the Jylhis Emacs build and, optionally, run a
# per-user daemon — systemd user service on Linux, launchd agent on macOS.
{
  lib,
  pkgs,
  config,
  ...
}:

let
  cfg = config.programs.emacs-jylhis;
  daemonArgs = [ "${cfg.finalPackage}/bin/emacs" "--fg-daemon" ] ++ cfg.daemon.extraOptions;
in
{
  imports = [ ./program.nix ];

  config = lib.mkIf cfg.enable (
    lib.mkMerge [
      {
        home.packages = [ cfg.finalPackage ];

        home.sessionVariables = lib.mkIf cfg.defaultEditor {
          EDITOR = "emacsclient";
        };
      }

      # Linux: systemd user service (home-manager uses native unit casing).
      (lib.mkIf (cfg.daemon.enable && pkgs.stdenv.hostPlatform.isLinux) {
        systemd.user.services.emacs = {
          Unit = {
            Description = "Emacs: the extensible, self-documenting text editor";
            Documentation = "info:emacs man:emacs(1)";
          };
          Service = {
            Type = "notify";
            ExecStart = lib.escapeShellArgs daemonArgs;
            ExecStop = "${cfg.finalPackage}/bin/emacsclient --eval (kill-emacs)";
            Restart = "on-failure";
            SuccessExitStatus = 15;
          };
          Install.WantedBy = [ "default.target" ];
        };
      })

      # macOS: launchd user agent.
      (lib.mkIf (cfg.daemon.enable && pkgs.stdenv.hostPlatform.isDarwin) {
        launchd.agents.emacs = {
          enable = true;
          config = {
            ProgramArguments = daemonArgs;
            RunAtLoad = true;
            KeepAlive = true;
          };
        };
      })
    ]
  );
}
