# Formatter config for the Nix layer only.  Upstream Emacs sources (C, Elisp,
# Texinfo) are deliberately excluded; they follow GNU style, not nixfmt.
_: {
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
    # Only format files under nix/ and the flake; ignore the Emacs tree.
    "src/*"
    "lisp/*"
    "lib/*"
    "lib-src/*"
    "test/*"
    "doc/*"
    "etc/*"
    "admin/*"
    "leim/*"
  ];
}
