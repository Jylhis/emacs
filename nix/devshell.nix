# Development shell for hacking on Emacs itself with fast, file-level
# incremental rebuilds — the thing pure Nix derivations cannot give.
#
# Workflow:
#   nix develop
#   ./autogen.sh
#   ./configure --with-native-compilation=default <flags>
#   make -j$(nproc)            # edit a file, re-run make -> only deps rebuild
#
# On Linux the C compiler is wrapped with ccache (a persistent cache that the
# pure build sandbox cannot use), so C recompiles after a clean are near
# instant.  On Darwin the compiler is left as the wrapped clang: forcing gcc
# breaks the NS/Cocoa port, and there is no libgccjit there anyway.
{
  pkgs,
  lib,
  emacs-jylhis,
}:

let
  isLinux = pkgs.stdenv.hostPlatform.isLinux;
in
pkgs.mkShell (
  {
    # Pull in every build/runtime dependency of the real package.
    inputsFrom = [ emacs-jylhis ];

    packages = with pkgs; [
      autoconf
      automake
      texinfo
      pkg-config
      ccache
    ];

    shellHook = ''
      export CCACHE_DIR="''${CCACHE_DIR:-$PWD/.ccache}"
      echo "emacs-jylhis dev shell — incremental build:"
      echo "  ./autogen.sh && ./configure --with-native-compilation=default && make -j"
    '';
  }
  // lib.optionalAttrs isLinux {
    # Force the ccache-wrapped gcc (Meson/Make split CC on whitespace and
    # treat argv[0] as the launcher).
    CC = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "cc"}";
    CXX = "${lib.getExe pkgs.ccache} ${lib.getExe' pkgs.gcc "c++"}";
    # Runtime native-comp shells out to the gcc driver, which is not the
    # cc-wrapper and otherwise can't find crti.o / libgcc_s.
    LIBRARY_PATH = lib.makeLibraryPath [
      pkgs.stdenv.cc.cc
      pkgs.stdenv.cc.libc
    ];
  }
)
