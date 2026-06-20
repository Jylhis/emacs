# Standalone build of the lib-src helper programs (emacsclient, etags, ctags,
# ebrowse, hexl, …).  These are independent of temacs/the dumped Emacs — they
# need only config.h + libgnu.a — so they live in their own small derivation
# that does not rebuild when the Emacs C core or the Lisp tree changes (the
# source is filtered to exclude src/*.c and *.el).
{
  lib,
  stdenv,
  autoconf,
  automake,
  texinfo,
  pkg-config,
  ncurses,
  root,
  version ? "32.0.50",
}:

stdenv.mkDerivation {
  pname = "emacs-jylhis-lib-src";
  inherit version;

  src = import ./build-filter.nix { inherit lib root; };

  nativeBuildInputs = [
    autoconf
    automake
    texinfo
    pkg-config
  ];
  buildInputs = [ ncurses ];

  # Minimal configuration: the helper programs need none of the GUI / native
  # compilation / library features, so disable them for a small, fast build.
  configureFlags = [
    "--without-native-compilation"
    "--without-x"
    "--with-toolkit=none"
    "--without-tree-sitter"
    "--without-gnutls"
    "--without-json"
    "--without-modules"
    "--without-xml2"
    "--without-sqlite3"
    "--without-mailutils"
    "--without-selinux"
    "--without-dbus"
  ];

  preConfigure = ''
    ./autogen.sh
  '';

  # Build gnulib (libgnu.a) then the lib-src programs only.
  buildPhase = ''
    runHook preBuild
    make -C lib -j$NIX_BUILD_CORES
    make -C lib-src -j$NIX_BUILD_CORES
    runHook postBuild
  '';

  # Install the user-facing programs that were produced.
  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin
    for p in emacsclient etags ctags ebrowse hexl rcs2log; do
      if [ -x "lib-src/$p" ]; then
        install -m0755 "lib-src/$p" "$out/bin/$p"
      fi
    done
    runHook postInstall
  '';

  meta = {
    description = "GNU Emacs helper programs (emacsclient, etags, …), built standalone";
    mainProgram = "emacsclient";
  };
}
