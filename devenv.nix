{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = with pkgs; [
    # Nix tooling
    nil
    nixfmt

    # Nix linting
    statix
    deadnix

    # Build dependencies for GNU Emacs
    autoconf
    automake
    pkg-config
    texinfo
    gnutls
    jansson
    libxml2
    ncurses
    sqlite

    # Debugging
    gdb
  ];

  # https://devenv.sh/languages/
  languages = {
    nix.enable = true;
    c.enable = true;
  };

  # https://devenv.sh/binary-caching/
  cachix = {
    enable = true;
    pull = [ "jylhis" ];
  };

  # https://devenv.sh/integrations/claude-code/
  claude.code.enable = true;

  # https://devenv.sh/scripts/
  scripts = {
    emacs-bootstrap = {
      description = "Full clean build from scratch (autogen + configure + make).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        ./autogen.sh
        ./configure --enable-checking='yes,glyphs' \
                    --enable-check-lisp-object-type \
                    CFLAGS='-O0 -g3'
        make -j$(nproc)
      '';
    };

    emacs-rebuild = {
      description = "Incremental rebuild (just make).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        make -j$(nproc)
      '';
    };

    emacs-check = {
      description = "Run the test suite (sequential, no -j).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        make check
      '';
    };

    emacs-run = {
      description = "Launch the locally built Emacs with -Q (no user config).";
      exec = ''
        set -euo pipefail
        "$DEVENV_ROOT/src/emacs" -Q "$@"
      '';
    };
  };

  # https://devenv.sh/tests/
  enterTest = ''
    set -euo pipefail
    echo "Running devenv tests"
    git --version | grep --color=auto "${pkgs.git.version}"
    gcc --version | head -1
    pkg-config --version
  '';

  # See full reference at https://devenv.sh/reference/options/
}
