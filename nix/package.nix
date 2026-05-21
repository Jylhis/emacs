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
  libxkbcommon,
  wayland,
  xorg,

  darwin,

  src ? lib.cleanSource ../.,
  version ? "31.0.50",

  withNativeCompilation ? stdenv.buildPlatform.canExecute stdenv.hostPlatform,
  withTreeSitter ? true,
  withSqlite3 ? true,
  withMailutils ? true,
  withModules ? true,
  withImageMagick ? false,
  withXwidgets ? false,

  noGui ? false,
  withPgtk ? false,
  withGTK3 ? stdenv.isLinux && !noGui && !withPgtk,
  withNS ? stdenv.isDarwin && !noGui,

  withSystemAppearancePatch ? false,
  withRoundUndecoratedPatch ? false,

  extraMesonFlags ? [ ],
  extraPatches ? [ ],
  siteStart ? null,
}:

let
  inherit (lib) optional optionals optionalString;

  toolkit =
    if noGui || withNS then
      "none"
    else if withPgtk then
      "pgtk"
    else if withGTK3 then
      "gtk3"
    else
      "none";

  darwinFrameworks = lib.optionals stdenv.isDarwin (
    with darwin.apple_sdk.frameworks;
    [
      AppKit
      Carbon
      Cocoa
      IOKit
      ImageIO
      OSAKit
      Quartz
      QuartzCore
      GSS
    ]
    ++ optional withXwidgets WebKit
  );

  patchPath = name: ./patches/${name};
  patchExists = name: builtins.pathExists (patchPath name);
in

stdenv.mkDerivation (finalAttrs: {
  pname =
    "emacs-jylhis"
    + optionalString noGui "-nox"
    + optionalString (withPgtk && !noGui) "-pgtk"
    + optionalString (withGTK3 && !withPgtk && !noGui && stdenv.isLinux) "-gtk3";

  inherit version src;

  patches =
    optional (withSystemAppearancePatch && patchExists "system-appearance.patch") (
      patchPath "system-appearance.patch"
    )
    ++ optional (withRoundUndecoratedPatch && patchExists "round-undecorated-frame.patch") (
      patchPath "round-undecorated-frame.patch"
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

  buildInputs =
    [
      gnutls
      libxml2
      ncurses
      gmp
      lcms2
      zlib
      gawk
      cairo
      pango
      fontconfig
      freetype
      harfbuzz
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
        ++ (with xorg; [
          libX11
          libXfixes
          libXrender
          libXrandr
          libXcomposite
          libXinerama
          libXi
          libXext
          libXtst
          libXft
          libxcb
          libxt
          libSM
          libICE
        ])
      )
      ++ optionals withPgtk [
        gtk3
        libxkbcommon
        wayland
      ]
    )
    ++ darwinFrameworks;

  mesonFlags =
    [
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
      (lib.mesonEnable "xwidgets" withXwidgets)
      (lib.mesonEnable "imagemagick" withImageMagick)
    ]
    ++ extraMesonFlags;

  enableParallelBuilding = true;

  postPatch = optionalString (siteStart != null) ''
    install -m0644 ${siteStart} lisp/site-start.el
  '';

  postInstall =
    optionalString (stdenv.isLinux && !noGui) ''
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
