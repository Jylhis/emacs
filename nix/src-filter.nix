{ lib, root }:

lib.cleanSourceWith {
  src = lib.cleanSource root;
  name = "emacs-jylhis-source";
  filter =
    path: _type:
    let
      baseName = baseNameOf (toString path);
    in
    !(builtins.elem baseName [
      ".direnv"
      ".devenv"
      ".envrc"
      ".envrc.local"
      "build"
      "flake.nix"
      "flake.lock"
      "default.nix"
      ".claude"
      "nix"
    ])
    && !(lib.hasPrefix "result" baseName)
    && !(lib.hasSuffix ".lock" baseName);
}
