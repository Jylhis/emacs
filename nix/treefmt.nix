{
  projectRootFile = "flake.nix";

  programs = {
    nixfmt.enable = true;
    deadnix.enable = true;
    statix.enable = true;
  };

  settings.global.excludes = [
    "*.lock"
    "*.patch"
    "*.el"
    "*.c"
    "*.h"
    "*.m"
    "*.texi"
    "*.texinfo"
    "etc/**"
    "lisp/**"
    "src/**"
    "lib/**"
    "lib-src/**"
    "test/**"
    "doc/**"
    "admin/**"
    "build-aux/**"
    "meson/**"
  ];
}
