{
  lib,
  stdenv,
  makeWrapper,

  autoconf,
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
  sigtool,

  src ? lib.cleanSource ../.,
  version ? "32.0.50",

  withNativeCompilation ? stdenv.buildPlatform.canExecute stdenv.hostPlatform,
  withTreeSitter ? true,
  withSqlite3 ? true,
  withMailutils ? stdenv.isLinux,
  withModules ? true,
  withXwidgets ? false,

  noGui ? false,
  withPgtk ? false,
  withGTK3 ? stdenv.isLinux && !noGui && !withPgtk,
  withNS ? stdenv.isDarwin && !noGui,

  extraConfigureFlags ? [ ],
  extraPatches ? [ ],
  siteStart ? null,
}:

let
  inherit (lib) optional optionals optionalString;

  withX = stdenv.isLinux && !noGui && !withPgtk;
in

stdenv.mkDerivation (_finalAttrs: {
  pname =
    "emacs-jylhis"
    + optionalString noGui "-nox"
    + optionalString (withPgtk && !noGui) "-pgtk"
    + optionalString (withGTK3 && !withPgtk && !noGui && stdenv.isLinux) "-gtk3"
    + optionalString (withNS && stdenv.isDarwin) "-macos";

  inherit version src;

  patches = extraPatches;

  nativeBuildInputs = [
    autoconf
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
    lcms2
    zlib
    gawk
  ]
  ++ optionals (!noGui) [
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
  ++ optionals stdenv.isLinux (
    [
      acl
      dbus
      glib
    ]
    ++ optional withNativeCompilation libgccjit
    ++ optionals withX [
      gtk3
      libx11
      libxfixes
      libxrender
      libxrandr
      libxcomposite
      libxinerama
      libxi
      libxext
      libxtst
      libxft
      libxcb
      libxt
      libsm
      libice
    ]
    ++ optionals withPgtk [
      gtk3
      libxkbcommon
      wayland
    ]
  )
  ++ optionals stdenv.isDarwin [ apple-sdk ]
  ++ optionals (stdenv.isDarwin && withNS) [ sigtool ];

  # The git tree carries no pre-generated configure script.
  preConfigure = ''
    ./autogen.sh
  '';

  configureFlags = [
    (if withNativeCompilation then "--with-native-compilation=aot" else "--without-native-compilation")
    (if withTreeSitter then "--with-tree-sitter" else "--without-tree-sitter")
    (if withSqlite3 then "--with-sqlite3" else "--without-sqlite3")
    (if withMailutils then "--with-mailutils" else "--without-mailutils")
    (if withModules then "--with-modules" else "--without-modules")
    (if withXwidgets then "--with-xwidgets" else "--without-xwidgets")
  ]
  ++ (
    if noGui then
      [
        "--without-x"
        "--without-ns"
      ]
    else if withNS then
      [
        "--with-ns"
        "--disable-ns-self-contained"
      ]
    else if withPgtk then
      [ "--with-pgtk" ]
    else
      [
        "--with-x-toolkit=gtk3"
        "--with-xft"
      ]
  )
  ++ extraConfigureFlags;

  enableParallelBuilding = true;

  postPatch = optionalString (siteStart != null) ''
    install -m0644 ${siteStart} lisp/site-start.el
  '';

  postInstall = optionalString (stdenv.isDarwin && withNS) ''
    mkdir -p $out/Applications
    mv nextstep/Emacs.app $out/Applications
    ln -snf $out/Applications/Emacs.app/Contents/MacOS/Emacs $out/bin/emacs
  '';

  meta = {
    description = "GNU Emacs from the jylhis/emacs fork";
    homepage = "https://github.com/Jylhis/emacs";
    license = lib.licenses.gpl3Plus;
    mainProgram = "emacs";
    platforms = lib.platforms.linux ++ lib.platforms.darwin;
  };
})
