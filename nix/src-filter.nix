# Filter the working tree down to the sources that affect the Emacs build,
# so a dirty dev checkout (build artifacts, the nix/ layer itself, editor
# droppings) neither enters the store nor invalidates the derivation hash.
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
      "result"
    ])
    && !(lib.hasPrefix "result" baseName)
    && !(lib.hasSuffix ".lock" baseName)
    # Stray autotools / build outputs that a hacking checkout accumulates.
    && !(builtins.elem baseName [
      "configure"
      "config.status"
      "config.log"
      "autom4te.cache"
    ])
    && !(lib.hasSuffix ".elc" baseName)
    && !(lib.hasSuffix ".eln" baseName);
}
