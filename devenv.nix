{ pkgs, lib, ... }:

let
  installDir = "$DEVENV_ROOT/.emacs-dev";
in
{
  # https://devenv.sh/packages/
  packages =
    # Cross-platform core: build tools, portable libraries,
    # and the text/image stack that compiles on both Linux and Darwin.
    (with pkgs; [
      # Build dependencies for GNU Emacs
      texinfo
      gnutls
      jansson
      libxml2
      ncurses
      sqlite

      # Meson + Ninja + Python (for the new build system; see PR #3)
      meson
      ninja
      python3

      # Text/image stack used by both X11/GTK and NS/Cocoa builds
      cairo
      pango
      fontconfig
      freetype
      harfbuzz

      # Image libraries
      libjpeg
      libtiff
      giflib
      libpng
      librsvg
      libwebp

      # Tree-sitter (modern syntax parsing)
      tree-sitter

      # Bignum support (GMP)
      gmp

      # Other useful libraries
      lcms2
      zlib
      gawk

      # Debugging
      # gdb
    ])
    # Linux-only: X11/GTK toolkit, Linux POSIX ACL/xattr, D-Bus, and
    # libgccjit for native compilation.  On macOS the NS/Cocoa build
    # supplies the GUI stack from the Apple SDK, and `acl` transitively
    # pulls `attr` which fails to build against macOS xattr headers.
    ++ lib.optionals pkgs.stdenv.isLinux (with pkgs; [
      acl
      dbus
      libgccjit
      gtk3
      xorg.libX11
      xorg.libXfixes
      xorg.libXrender
      xorg.libXrandr
      xorg.libXcomposite
      xorg.libXinerama
      xorg.libXi
      xorg.libXext
      xorg.libXtst
      xorg.libXft
      xorg.libXt
      xorg.libSM
      xorg.libICE
    ]);

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

    # ---- Meson build ----
    meson-setup = {
      description = "Configure the meson build dir.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        meson setup build
      '';
    };
    meson-build = {
      description = "Build all default Meson targets (lib-src + temacs etc.).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        meson compile -C build
      '';
    };
    meson-pdmp = {
      description = "Run the full Meson dump cycle (compile-main + emacs.pdmp).";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        meson compile -C build emacs.pdmp
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
