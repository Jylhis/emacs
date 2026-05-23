{ pkgs, externalPackages }:
# Produces an "overlay tree" derivation: a directory whose contents,
# when copied (rsync-style) onto the Emacs source tree, materialize
# every externally-developed component at its canonical location.
#
# Schema is dictated by nix/external-packages.nix entries:
#
#   src         derivation | null
#   destination string     | null
#                 "lisp/foo/"            -> dest is a directory; copy
#                                            all files in src (optionally
#                                            filtered by `files`) into it
#                 "lisp/foo/bar.el"      -> dest is a file path; copy
#                                            src/<basename-of-dest> there
#   files       list of relative path globs inside src to include
#               (only meaningful for directory destinations)
#
# Entries with src == null or destination == null are skipped, so the
# inventory file can be migrated incrementally.

let
  inherit (pkgs) lib runCommand;

  staged = lib.filterAttrs
    (_: e: e ? src && e.src != null && e ? destination && e.destination != null)
    externalPackages;

  isDirDest = d: lib.hasSuffix "/" d;

  manifestEntries = lib.mapAttrsToList
    (name: e: {
      inherit name;
      destination = e.destination;
      kind = if isDirDest e.destination then "tree" else "file";
      files = e.files or null;
    })
    staged;

  manifestJson = builtins.toJSON {
    schema = 1;
    entries = manifestEntries;
  };

  copyEntry = name: e:
    let
      dest = e.destination;
      files = e.files or null;
    in
      if isDirDest dest then
        # Directory destination; copy filtered/full src into $out/<dest>.
        ''
          mkdir -p "$out/${dest}"
          ${if files == null then
              ''cp -r "${e.src}"/. "$out/${dest}"''
            else
              lib.concatMapStringsSep "\n"
                (g: ''
                  shopt -s nullglob
                  for f in "${e.src}"/${g}; do
                    cp -r "$f" "$out/${dest}"
                  done
                  shopt -u nullglob
                '')
                files}
        ''
      else
        # File destination; copy src/<basename> to $out/<dest>.
        ''
          mkdir -p "$(dirname "$out/${dest}")"
          cp "${e.src}/${baseNameOf dest}" "$out/${dest}"
        '';

  copyAll = lib.concatStringsSep "\n"
    (lib.mapAttrsToList copyEntry staged);

in
runCommand "emacs-external-sources" {
  passthru = { manifest = manifestEntries; };
} ''
  mkdir -p "$out"
  cat > "$out/_manifest.json" <<'JSON'
${manifestJson}
JSON
  ${copyAll}
''
