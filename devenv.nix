{ pkgs, ... }:

let
  installDir = "$DEVENV_ROOT/.emacs-dev";
in
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

    # Image libraries
    libjpeg
    libtiff
    giflib
    libpng
    librsvg
    libwebp

    # Tree-sitter (modern syntax parsing)
    tree-sitter

    # Native compilation (Emacs Lisp -> native code)
    libgccjit

    # Text shaping
    harfbuzz

    # Bignum support (GMP)
    gmp

    # Other useful libraries
    lcms2
    dbus
    zlib

    # Debugging
    # gdb
  ];

  # https://devenv.sh/languages/
  languages = {
    nix.enable = true;
    c.enable = true;
    java.enable = true;
    shell.enable = true;
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
    emacs-min = {
      description = "Minimal emacs";
      exec = ''
        ./configure \
        -C \
        --disable-year2038 \
        --disable-xattr \
        --disable-acl \
        --without-selinux \
        --without-all \
        --with-x-toolkit=no \
        --without-cairo \
        --without-gnutls \
        --without-xml2 \
        --without-imagemagick \
        --without-xpm \
        --without-jpeg \
        --without-tiff \
        --without-gif \
        --without-png \
        --without-rsvg \
        --without-webp \
        --without-lcms2 \
        --without-dbus \
        --without-gconf \
        --without-gsettings \
        --without-selinux \
        --without-sound \
        --without-tree-sitter \
        --without-native-compilation \
        --with-x=no \
        --disable-largefile \
        --disable-ns-self-contained \
        --disable-build-details
      '';
    };
    emacs-bootstrap = {
      description = "Full clean build from scratch (autogen + configure + make).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        ./autogen.sh
        ./configure --prefix=${installDir} \
                    --enable-checking='yes,glyphs' \
                    --enable-check-lisp-object-type \
                    --with-native-compilation \
                    --with-tree-sitter \
                    --with-xwidgets \
                    --with-modules \
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

    emacs-install = {
      description = "Install into ${installDir}.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        make install
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

    emacs-check-file = {
      description = "Run tests for a single file, e.g. emacs-check-file lisp/foo/bar";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        if [ -z "''${1:-}" ]; then
          echo "Usage: emacs-check-file <path>"
          echo "  e.g. emacs-check-file lisp/simple"
          exit 1
        fi
        make -C test "$1-tests"
      '';
    };

    emacs-run = {
      description = "Launch the locally built Emacs with -Q (no user config).";
      exec = ''
        set -euo pipefail
        "$DEVENV_ROOT/src/emacs" -Q "$@"
      '';
    };

    emacs-run-installed = {
      description = "Launch the installed Emacs with -Q (no user config).";
      exec = ''
        set -euo pipefail
        "${installDir}/bin/emacs" -Q "$@"
      '';
    };

    emacs-distclean = {
      description = "Full clean (remove all build artifacts, requires re-bootstrap).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        if [ -f Makefile ]; then
          make distclean
        else
          echo "No Makefile found; nothing to clean."
        fi
      '';
    };

    emacs-configure = {
      description = "Re-run configure with debug flags (no autogen, no make).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        ./configure --prefix=${installDir} \
                    --enable-checking='yes,glyphs' \
                    --enable-check-lisp-object-type \
                    --with-native-compilation \
                    --with-tree-sitter \
                    --with-xwidgets \
                    --with-modules \
                    CFLAGS='-O0 -g3'
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
