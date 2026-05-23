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
    # libgccjit for native compilation.  (`acl` transitively pulls
    # `attr` which fails to build against macOS xattr headers, so it
    # stays out of the Darwin set.)
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
    ])
    # Darwin-only: unified Apple SDK supplies the AppKit / Cocoa /
    # Carbon / IOKit / Quartz frameworks the NS port's .m sources
    # include.  The Nix-wrapped cc picks up apple-sdk's sdkroot as
    # -isysroot, so #import <AppKit/AppKit.h> resolves without any
    # explicit -iframework plumbing.  sigtool is needed to ad-hoc
    # sign the resulting binary (matches nixpkgs make-emacs.nix).
    ++ lib.optionals pkgs.stdenv.isDarwin (with pkgs; [
      apple-sdk
      darwin.sigtool
    ]);

  # https://devenv.sh/languages/
  languages = {
    nix.enable = true;
    c.enable = true;
    java.enable = true;
    shell.enable = true;
  };

  # On Linux, `libgccjit` in the packages list puts an *unwrapped*
  # `gcc` first on PATH and shadows the gcc-wrapper from
  # `languages.c.enable`.  meson probes the compiler via `gcc`, so it
  # picks the unwrapped one whose link line has no
  # `-L /nix/store/.../glibc/lib` and fails with "cannot find Scrt1.o".
  # Force CC/CXX/OBJC at the wrapped GCC by absolute store path so
  # they're picked regardless of PATH order.
  #
  # On Darwin there's no libgccjit (no native compilation here) and
  # the .m sources need clang to resolve `#import <AppKit/AppKit.h>`
  # via the SDKROOT-driven framework search path -- forcing GCC
  # breaks the NS / Cocoa port.  Leave CC/CXX/OBJC unset there so the
  # default Darwin stdenv clang (which `languages.c.enable` and the
  # apple-sdk buildInput already wire up) handles every TU.
  #
  # ccache is prepended as a compiler launcher.  Meson splits CC on
  # whitespace and treats argv[0] as the launcher, so this works
  # without any meson.build changes.  ccache execs the wrapped cc
  # with the original env, so NIX_LDFLAGS / NIX_CC_WRAPPER_* stay
  # live.  Defaults: ~/.cache/ccache, 5 GB max -- override with
  # CCACHE_DIR / CCACHE_MAXSIZE if needed.
  env = lib.optionalAttrs pkgs.stdenv.isLinux {
    CC = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}";
    CXX = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "c++"}";
    OBJC = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}";
  };

  enterShell =
    (lib.optionalString pkgs.stdenv.isLinux ''
      export CC="${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}"
      export CXX="${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "c++"}"
      export OBJC="${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}"
    '')
    + ''
      # Hash compile commands relative to the project root so the
      # cache survives moving the checkout or building from a
      # worktree.  Must live in enterShell because $DEVENV_ROOT is
      # only defined at runtime (the `env` block is static nix).
      export CCACHE_BASEDIR="$DEVENV_ROOT"
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
