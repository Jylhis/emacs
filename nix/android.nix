{
  lib,
  stdenv,
  meson,
  ninja,
  pkg-config,
  python3,
  m4,
  jdk17_headless,
  androidComposition,
  src,
  emacsHost,
  version ? "31.0.50",
  androidApi ? 29,
}:

let
  androidSdk = "${androidComposition.androidsdk}/libexec/android-sdk";
  androidNdk = "${androidSdk}/ndk-bundle";

  # Write the cross file inline so the NDK toolchain bin dir from
  # androidComposition can be wired into [binaries] without forcing
  # users to edit a tracked file.  The actual --target / --sysroot /
  # API-level flags flow through -Dandroid-* meson options.
  crossFile = builtins.toFile "android.cross" ''
    [host_machine]
    system     = 'android'
    cpu_family = 'aarch64'
    cpu        = 'aarch64'
    endian     = 'little'

    [binaries]
    c          = '${androidNdk}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang'
    cpp        = '${androidNdk}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang++'
    ar         = '${androidNdk}/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-ar'
    strip      = '${androidNdk}/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip'
    ranlib     = '${androidNdk}/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-ranlib'
    objcopy    = '${androidNdk}/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-objcopy'
    pkg-config = 'false'

    [properties]
    needs_exe_wrapper = true
  '';
in

stdenv.mkDerivation {
  pname = "emacs-jylhis-android";
  inherit version src;

  nativeBuildInputs = [
    meson
    ninja
    pkg-config
    python3
    m4
    jdk17_headless
    androidComposition.androidsdk
  ];

  # Re-point the cross file's NDK path at the linux-x86_64 host
  # toolchain; the file above is a plain text store-path so no edit
  # is needed at build time.
  configurePhase = ''
    runHook preConfigure

    # Stage the host build dir (bootstrap-emacs, emacs.pdmp,
    # byte-compiled lisp) into a writable copy that meson can read.
    cp -R ${emacsHost}/share/emacs/host-build ./host-build
    chmod -R u+w host-build

    meson setup build-android \
      --cross-file=${crossFile} \
      -Dandroid=enabled \
      -Dandroid-ndk=${androidNdk} \
      -Dandroid-sdk=${androidSdk} \
      -Dandroid-api=${toString androidApi} \
      -Dandroid-host-build=$PWD/host-build \
      -Dnative-compilation=no \
      -Dgnutls=disabled \
      -Dtree-sitter=disabled \
      -Dsqlite3=disabled \
      -Dxml2=disabled

    runHook postConfigure
  '';

  buildPhase = ''
    runHook preBuild
    meson compile -C build-android apk
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    install -Dm0644 build-android/emacs-*-aarch64.apk \
      $out/share/emacs-jylhis-android.apk
    runHook postInstall
  '';

  meta = {
    description = "GNU Emacs 31 Android APK (Jylhis fork) -- aarch64, minimal first cut";
    longDescription = ''
      Cross-compiled Android application package built from the
      Jylhis fork via Meson + the Android NDK.  This first cut
      ships a minimal Emacs with no TLS, no images, no tree-sitter
      and no native compilation; revivals of those features wait
      on the parked cross/ndk-build module system that consumes the
      prebuilt third-party libs from admin/download-android-deps.sh.
    '';
    homepage = "https://github.com/Jylhis/emacs";
    license = lib.licenses.gpl3Plus;
    platforms = [ "x86_64-linux" "aarch64-linux" ];
    maintainers = [ ];
  };
}
