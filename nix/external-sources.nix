#  nix/external-sources.nix --- staging derivation for vendored externals
#
#  Consumes nix/external-packages.nix.  For every entry with a non-null
#  `src` and a non-null `destination`, materializes the fetched source at
#  the given path under `$out`, suitable for `cp -rL` into the Emacs
#  source tree from `nix/package.nix`'s `postPatch`.
#
#  Per-entry shape:
#    src         a fetched derivation (fetchurl, fetchFromGitHub, ...)
#    destination repo-relative path in the Emacs tree (file or dir)
#    files       optional list of paths *inside* `src` to copy.  When
#                set, `destination` is treated as a directory and each
#                file is placed there with its upstream basename.  When
#                unset, the whole `src` directory is copied to
#                `destination`.
#
#  No FOD; this is `runCommandLocal`.  Each `src` fetch is its own
#  derivation already.
{ pkgs }:
let
  inherit (pkgs) lib;
  inventory = import ./external-packages.nix { inherit pkgs; };
  selected = lib.filterAttrs (
    _name: e: (e.src or null) != null && (e.destination or null) != null
  ) inventory;
  copyOne =
    _name: e:
    let
      files = e.files or null;
    in
    if files == null then
      ''
        mkdir -p "$(dirname "$out/${e.destination}")"
        cp -rL "${e.src}" "$out/${e.destination}"
        chmod -R u+w "$out/${e.destination}"
      ''
    else
      ''
        mkdir -p "$out/${e.destination}"
      ''
      + lib.concatMapStringsSep "\n" (f: ''
        cp -L "${e.src}/${f}" "$out/${e.destination}/$(basename "${f}")"
      '') files
      + ''
        chmod -R u+w "$out/${e.destination}"
      '';
  body = lib.concatStringsSep "\n" (lib.mapAttrsToList copyOne selected);
in
pkgs.runCommandLocal "emacs-external-sources"
  {
    passthru = {
      inherit selected;
      entries = lib.attrNames selected;
    };
  }
  (
    if body == "" then
      ''
        mkdir -p "$out"
      ''
    else
      ''
        mkdir -p "$out"
        ${body}
      ''
  )
