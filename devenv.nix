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

      # Compiler cache: wraps cc/c++ via CC/CXX below so repeated
      # builds of the same translation unit are hashed and reused.
      ccache

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

      # Upstream-commit-review skill: syntax-aware merge driver,
      # syntax-aware diff renderer, and incremental-merge fallback used
      # by .claude/skills/upstream-commit-review/
      mergiraf
      difftastic
      git-imerge

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
      libxt
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

  # The `libgccjit` package in the packages list above puts an
  # *unwrapped* `gcc` first on PATH, which shadows the gcc-wrapper
  # provided by `languages.c.enable`.  meson probes the compiler
  # via `gcc`, so it picks the unwrapped one whose link line has
  # no `-L /nix/store/.../glibc/lib` and fails with "cannot find
  # Scrt1.o".  Point CC/CXX at the wrapped binaries by absolute
  # store path so they're picked regardless of PATH order or what
  # `languages.c.enable`'s own enterShell sets.
  #
  # ccache is prepended as a compiler launcher.  Meson splits CC on
  # whitespace and treats argv[0] as the launcher, so this works
  # without any meson.build changes.  ccache execs the wrapped cc
  # with the original env, so NIX_LDFLAGS / NIX_CC_WRAPPER_* stay
  # live.  Defaults: ~/.cache/ccache, 5 GB max -- override with
  # CCACHE_DIR / CCACHE_MAXSIZE if needed.
  env = {
    CC = "${pkgs.ccache}/bin/ccache ${pkgs.gcc}/bin/cc";
    CXX = "${pkgs.ccache}/bin/ccache ${pkgs.gcc}/bin/c++";
  };

  enterShell = ''
    export CC="${pkgs.ccache}/bin/ccache ${pkgs.gcc}/bin/cc"
    export CXX="${pkgs.ccache}/bin/ccache ${pkgs.gcc}/bin/c++"
  '';

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
    cc --version | head -1
    ccache --version | head -1
    pkg-config --version
  '';

  # See full reference at https://devenv.sh/reference/options/
}
