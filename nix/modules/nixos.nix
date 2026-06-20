# NixOS module: install the Jylhis Emacs build and, optionally, run it as a
# per-user systemd daemon.  Mirrors the unit shape of nixpkgs'
# nixos/modules/services/editors/emacs.nix.
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
      EDITOR = lib.mkOverride 900 "emacsclient";
    };

    systemd.user.services.emacs = lib.mkIf cfg.daemon.enable {
      description = "Emacs: the extensible, self-documenting text editor";
      documentation = [
        "info:emacs"
        "man:emacs(1)"
      ];
      serviceConfig = {
        Type = "notify";
        ExecStart = lib.escapeShellArgs (
          [
            "${cfg.finalPackage}/bin/emacs"
            "--fg-daemon"
          ]
          ++ cfg.daemon.extraOptions
        );
        ExecStop = "${cfg.finalPackage}/bin/emacsclient --eval (kill-emacs)";
        # emacsclient kills the daemon with SIGTERM (15); treat as success.
        Restart = "on-failure";
        SuccessExitStatus = 15;
      };
      wantedBy = [ "default.target" ];
    };
  };
}
