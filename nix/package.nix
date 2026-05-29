{
  lib,
  stdenv,
  makeWrapper,

  meson,
  ninja,
  pkg-config,
  texinfo,
  python3,

  gnutls,
  libxml2,
  ncurses,
  gmp,
  libgcrypt,
  lcms2,
  zlib,
  gawk,

  cairo,
  pango,
  fontconfig,
  freetype,
  harfbuzz,
  libjpeg,
  libtiff,
  giflib,
  libpng,
  librsvg,
  libwebp,

  tree-sitter,
  sqlite,
  mailutils,
  imagemagick,

  acl,
  dbus,
  libgccjit,
  glib,
  gtk3,
  libx11,
  libxfixes,
  libxrender,
  libxrandr,
  libxcomposite,
  libxinerama,
  libxi,
  libxext,
  libxtst,
  libxft,
  libxcb,
  libxt,
  libsm,
  libice,
  libxkbcommon,
  wayland,

  apple-sdk,

  src ? lib.cleanSource ../.,
  version ? "31.0.50",

  withNativeCompilation ? stdenv.buildPlatform.canExecute stdenv.hostPlatform,
  withTreeSitter ? true,
  withSqlite3 ? true,
  withMailutils ? stdenv.isLinux,
  withModules ? true,
  withImageMagick ? false,
  withXwidgets ? false,

  noGui ? false,
  withPgtk ? false,
  withGTK3 ? stdenv.isLinux && !noGui && !withPgtk,
  withNS ? stdenv.isDarwin && !noGui,
  withNsSelfContained ? false,

  withSystemAppearancePatch ? false,
  withRoundUndecoratedPatch ? false,
  withFixNsXColorsPatch ? false,

  extraMesonFlags ? [ ],
  extraPatches ? [ ],
  siteStart ? null,

  # When set, the resulting derivation keeps a copy of the meson
  # build dir at $out/share/emacs/host-build so a downstream
  # cross-compile (nix/android.nix) can read bootstrap-emacs,
  # emacs.pdmp, and the byte-compiled lisp tree.
  exposeHostBuild ? false,
}:

let
  inherit (lib) optional optionals optionalString;

  toolkit =
    if noGui then
      "none"
    else if withPgtk then
      "pgtk"
    else if withGTK3 then
      "gtk3"
    else
      "auto";

  darwinFrameworks = optional stdenv.isDarwin apple-sdk;

  patchPath = name: ./patches/${name};
  patchExists = name: builtins.pathExists (patchPath name);
in

stdenv.mkDerivation (_finalAttrs: {
  pname =
    "emacs-jylhis"
    + optionalString noGui "-nox"
    + optionalString (withPgtk && !noGui) "-pgtk"
    + optionalString (withGTK3 && !withPgtk && !noGui && stdenv.isLinux) "-gtk3"
    + optionalString (withNsSelfContained && stdenv.isDarwin) "-macos";

  inherit version src;

  patches =
    optional (withSystemAppearancePatch && patchExists "system-appearance.patch") (
      patchPath "system-appearance.patch"
    )
    ++ optional (withRoundUndecoratedPatch && patchExists "round-undecorated-frame.patch") (
      patchPath "round-undecorated-frame.patch"
    )
    ++ optional (withFixNsXColorsPatch && patchExists "fix-ns-x-colors.patch") (
      patchPath "fix-ns-x-colors.patch"
    )
    ++ extraPatches;

  nativeBuildInputs = [
    meson
    ninja
    pkg-config
    texinfo
    python3
    makeWrapper
  ];

  buildInputs = [
    gnutls
    libxml2
    ncurses
    gmp
    libgcrypt
    lcms2
    zlib
    gawk
    cairo
    pango
    fontconfig
    freetype
    harfbuzz
    libxft
    libjpeg
    libtiff
    giflib
    libpng
    librsvg
    libwebp
  ]
  ++ optional withSqlite3 sqlite
  ++ optional withTreeSitter tree-sitter
  ++ optional withMailutils mailutils
  ++ optional withImageMagick imagemagick
  ++ optionals stdenv.isLinux (
    [
      acl
      dbus
      glib
    ]
    ++ optional withNativeCompilation libgccjit
    ++ optionals (withGTK3 && !withPgtk) (
      [ gtk3 ]
      ++ [
        libx11
        libxfixes
        libxrender
        libxrandr
        libxcomposite
        libxinerama
        libxi
        libxext
        libxtst
        libxcb
        libxt
        libsm
        libice
      ]
    )
    ++ optionals withPgtk [
      gtk3
      libxkbcommon
      wayland
    ]
  )
  ++ darwinFrameworks;

  mesonFlags = [
    "-Dtoolkit=${toolkit}"
    "-Dnative-compilation=${if withNativeCompilation then "aot" else "no"}"
    "-Dcompress-install=true"
    "-Dbuild-details=false"
    (lib.mesonEnable "ns" withNS)
    (lib.mesonEnable "pgtk" withPgtk)
    (lib.mesonEnable "tree-sitter" withTreeSitter)
    (lib.mesonEnable "sqlite3" withSqlite3)
    (lib.mesonEnable "mailutils" withMailutils)
    (lib.mesonEnable "modules" withModules)
    (lib.mesonEnable "toolkit-scroll-bars" (withGTK3 || withPgtk || withNS))
    (lib.mesonEnable "xwidgets" withXwidgets)
    (lib.mesonEnable "imagemagick" withImageMagick)
    (lib.mesonEnable "dbus" stdenv.isLinux)
    (lib.mesonEnable "gpm" false)
    (lib.mesonEnable "gsettings" false)
    (lib.mesonEnable "libotf" false)
    (lib.mesonEnable "libsystemd" false)
    (lib.mesonEnable "m17n-flt" false)
    (lib.mesonEnable "selinux" false)
    (lib.mesonEnable "xdbe" (stdenv.isLinux && withGTK3 && !withPgtk))
    (lib.mesonEnable "xim" (stdenv.isLinux && withGTK3 && !withPgtk))
    (lib.mesonEnable "xinput2" (stdenv.isLinux && withGTK3 && !withPgtk))
  ]
  ++ optional withNsSelfContained (lib.mesonEnable "ns-self-contained" true)
  ++ extraMesonFlags;

  enableParallelBuilding = true;

  postPatch = optionalString (siteStart != null) ''
    install -m0644 ${siteStart} lisp/site-start.el
  '';

  postInstall =
    optionalString exposeHostBuild ''
      mkdir -p $out/share/emacs/host-build/src $out/share/emacs/host-build/lisp
      # bootstrap-emacs + the final pdumper image -- the Android APK
      # bundles emacs.pdmp under assets/, and the cross build re-uses
      # bootstrap-emacs to stage byte-compiled lisp.
      install -m0755 src/bootstrap-emacs $out/share/emacs/host-build/src/
      install -m0644 src/emacs.pdmp      $out/share/emacs/host-build/src/
      # Mirror the byte-compiled lisp tree (only .elc files).
      (cd lisp && find . -name '*.elc' -print0 \
        | xargs -0 -I {} install -Dm0644 {} \
            $out/share/emacs/host-build/lisp/{})
    ''
    + optionalString (stdenv.isLinux && !noGui) ''
      if [ -f etc/emacs.desktop ]; then
        install -Dm0644 etc/emacs.desktop \
          $out/share/applications/emacs.desktop
      fi
    ''
    + optionalString (stdenv.isDarwin && withNS) ''
      mkdir -p $out/Applications
      if [ -d nextstep/Emacs.app ]; then
        cp -R nextstep/Emacs.app $out/Applications/
      fi
    ''
    + optionalString withNativeCompilation ''
      if [ -f $out/bin/emacs ]; then
        wrapProgram $out/bin/emacs \
          --prefix LIBRARY_PATH : '${
            lib.makeLibraryPath [
              libgccjit
              stdenv.cc.cc
              zlib
            ]
          }' \
          --prefix PATH : '${lib.makeBinPath [ stdenv.cc.cc ]}'
      fi
    '';

  passthru = {
    inherit
      withNativeCompilation
      withTreeSitter
      withSqlite3
      withGTK3
      withPgtk
      withNS
      withXwidgets
      ;
    nativeComp = withNativeCompilation;
    treeSitter = withTreeSitter;
  };

  meta = {
    description = "GNU Emacs 31 from the Jylhis fork, built with Meson";
    longDescription = ''
      GNU Emacs 31.0.50 from the Jylhis development fork.  Builds via
      Meson + Ninja (this fork's only supported build system; autotools
      was removed at commit 313f867).  Variants are exposed via overlay
      attributes for GTK3, Pure GTK (Wayland), Cocoa NS (macOS), and a
      terminal-only build.  Native compilation and tree-sitter are on
      by default; macOS appearance / undecorated-frame patches from
      emacs-plus are opt-in.
    '';
    homepage = "https://github.com/Jylhis/emacs";
    license = lib.licenses.gpl3Plus;
    mainProgram = "emacs";
    platforms = lib.platforms.unix;
    maintainers = [ ];
  };
})
