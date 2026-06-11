{
  pkgs ? import <nixpkgs> { },
  withNativeCompilation ? null,
  withPgtk ? false,
  withGTK3 ? null,
  noGui ? false,
}:

let
  inherit (pkgs) lib;
  src = import ./nix/src-filter.nix {
    inherit lib;
    root = ./.;
  };
  args = lib.filterAttrs (_: v: v != null) {
    inherit src withPgtk noGui;
    inherit withNativeCompilation;
    inherit withGTK3;
  };
in
pkgs.callPackage ./nix/package.nix args
