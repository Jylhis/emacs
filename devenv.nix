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
      autoconf
      texinfo
      gnutls
      jansson
      libxml2
      ncurses
      sqlite

      # Python for the admin/ helper scripts
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

      # Admin tooling (spell-check, semantic C patches)
      codespell
      coccinelle

      # Debugging
      # gdb
    ])
    # Linux-only: X11/GTK toolkit, Linux POSIX ACL/xattr, D-Bus, and
    # libgccjit for native compilation.  (`acl` transitively pulls
    # `attr` which fails to build against macOS xattr headers, so it
    # stays out of the Darwin set.)
    ++ lib.optionals pkgs.stdenv.isLinux (
      with pkgs;
      [
        acl
        dbus
        libgccjit
        gtk3
        xorg.libX11
        xorg.libXpm
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
      ]
    )
    # Darwin-only: unified Apple SDK supplies the AppKit / Cocoa /
    # Carbon / IOKit / Quartz frameworks the NS port's .m sources
    # include.  The Nix-wrapped cc picks up apple-sdk's sdkroot as
    # -isysroot, so #import <AppKit/AppKit.h> resolves without any
    # explicit -iframework plumbing.  sigtool is needed to ad-hoc
    # sign the resulting binary (matches nixpkgs make-emacs.nix).
    ++ lib.optionals pkgs.stdenv.isDarwin (
      with pkgs;
      [
        apple-sdk
        darwin.sigtool
      ]
    );

  # https://devenv.sh/languages/
  languages = {
    nix.enable = true;
    c.enable = true;
    java.enable = true;
    shell.enable = true;
  };

  # On Linux, `libgccjit` in the packages list puts an *unwrapped*
  # `gcc` first on PATH and shadows the gcc-wrapper from
  # `languages.c.enable`.  configure probes the compiler via `gcc`,
  # so it picks the unwrapped one whose link line has no
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
  # ccache is prepended as a compiler launcher.  ccache execs the
  # wrapped cc with the original env, so NIX_LDFLAGS /
  # NIX_CC_WRAPPER_* stay live.  Defaults: ~/.cache/ccache, 5 GB max
  # -- override with CCACHE_DIR / CCACHE_MAXSIZE if needed.
  env = lib.optionalAttrs pkgs.stdenv.isLinux {
    CC = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}";
    CXX = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "c++"}";
    OBJC = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}";

    # Runtime native compilation: libgccjit shells out to the gcc
    # driver, which then invokes `ld` to link each .eln.  That driver
    # is *not* the cc-wrapper, so it cannot find the C runtime startup
    # files (crti.o, from glibc) or libgcc_s (from gcc's lib output)
    # on its own and fails with "cannot find crti.o" / "-lgcc_s".
    # LIBRARY_PATH points the driver at both.  Without this, any test
    # that redefines a primitive subr (which triggers an on-demand
    # trampoline native-compile, e.g. subr-tests-bug22027) fails.
    LIBRARY_PATH = lib.makeLibraryPath [
      pkgs.stdenv.cc.cc
      pkgs.stdenv.cc.libc
    ];
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

    # ---- Autotools build ----
    emacs-configure = {
      description = "Generate configure and run it with the dev install prefix.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        ./autogen.sh
        ./configure --prefix="${installDir}" "$@"
      '';
    };
    emacs-build = {
      description = "Build Emacs and the helper binaries with make.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)" "$@"
      '';
    };

    # ---- Test helpers ----
    emacs-test-file = {
      description = "Run ERT tests for one test file, e.g. emacs-test-file lisp/net/eww-tests";
      exec = ''
        set -euo pipefail
        FILE="''${1:?Usage: emacs-test-file <path under test/, without .el>}"
        cd "$DEVENV_ROOT"
        make -C test "''${FILE}"
      '';
    };

    # ---- Admin helpers ----
    emacs-codespell = {
      description = "Spell-check the source tree via codespell.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        codespell "$@"
      '';
    };

    emacs-bisect = {
      description = "Start a git bisect session using admin/git-bisect-start.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT"
        bash admin/git-bisect-start "$@"
      '';
    };

    # ---- Debug ----
    emacs-debug = {
      description = "Launch GDB (Linux) or LLDB (macOS) from src/ with auto-loaded init.";
      exec = ''
        set -euo pipefail
        cd "$DEVENV_ROOT/src"
        if command -v gdb >/dev/null 2>&1; then
          gdb --args ./emacs "$@"
        elif command -v lldb >/dev/null 2>&1; then
          lldb -- ./emacs "$@"
        else
          echo "Neither gdb nor lldb found in PATH" >&2
          exit 1
        fi
      '';
    };
  };

  # https://devenv.sh/tests/
  enterTest = ''
    set -euo pipefail
    echo "Running devenv tests"
    git --version
    cc --version | sed -n '1p'
    ccache --version | sed -n '1p'
    pkg-config --version
    autoconf --version | sed -n '1p'
    makeinfo --version | sed -n '1p'
  '';

  # See full reference at https://devenv.sh/reference/options/
}
