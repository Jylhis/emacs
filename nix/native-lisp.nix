# Separate ahead-of-time native-compilation derivation for the core + eln
# split.  `emacs-jylhis-core` ships only the preloaded .eln; this derivation
# AOT-compiles the rest of the bundled lisp into its own
# `$out/share/emacs/native-lisp/<abi>/` tree using the core binary.
#
# This works because Emacs' eln names are *relocation-independent*
# (`comp.c` rewrites the load-path prefix to `//` before hashing), so an .eln
# compiled here is found at runtime by core via `native-comp-eln-load-path`,
# which nixpkgs' site-start.el unions across NIX_PROFILES.  The two are cached
# independently; a lisp-only edit rebuilds just this.
#
# Notes on the two bugs that broke the first attempt:
#  - installed sources are gzip-compressed (*.el.gz), so we glob those.
#  - running the native compiler standalone needs LIBRARY_PATH pointed at
#    libgccjit's gcc lib dir (libemutls_w), which the runtime wrapper omits.
{
  runCommand,
  writeText,
  lib,
  libgccjit,
  stdenv,
  apple-sdk ? null,
  emacs-core,
  version ? "32.0.50",
}:

let
  lispDir = "${emacs-core}/share/emacs/${version}/lisp";
  coreEln = "${emacs-core}/lib/emacs/${version}/native-lisp";

  compileEl = writeText "emacs-jylhis-aot.el" ''
    (require 'comp)
    (let ((out (concat (getenv "out") "/share/emacs/native-lisp/"))
          (lispdir (getenv "lispDir"))
          (coreeln (getenv "coreEln")))
      ;; First (writable) entry receives new .eln; coreeln lets
      ;; `comp-lookup-eln' detect the preloaded set so we don't recompile it.
      (setq native-comp-eln-load-path (list out coreeln)
            native-comp-async-report-warnings-errors nil
            warning-minimum-level :error)
      (let ((n 0) (skipped 0))
        (dolist (f (directory-files-recursively lispdir "\\.el\\.gz\\'"))
          (cond
           ;; Already provided by core (preloaded) — skip to avoid collisions.
           ((comp-lookup-eln f) (setq skipped (1+ skipped)))
           ((string-match-p
             "/\\(loaddefs\\|ldefs-boot\\|leim-list\\|cus-load\\|finder-inf\\|subdirs\\)\\.el\\.gz\\'"
             f) nil)
           (t (condition-case err
                  (progn (native-compile f) (setq n (1+ n)))
                (error (message "skip %s: %S" f err))))))
        (message "native-lisp: compiled %d, skipped %d preloaded" n skipped)))
  '';
in
runCommand "emacs-jylhis-native-lisp-${version}"
  {
    inherit lispDir coreEln;
    meta = {
      description = "AOT native-compiled (.eln) Elisp for emacs-jylhis-core";
    };
  }
  ''
    # libgccjit shells out to a raw gcc driver to link each .eln; give it the
    # libraries the nix cc-wrapper would normally supply:
    #  - libgccjit's runtime (libemutls_w) in its lib/gcc/<triple>/<ver> dir,
    #  - on macOS, the SDK's libSystem,
    #  - on Linux, the C runtime / libgcc.
    export LIBRARY_PATH="${libgccjit}/lib/gcc:${libgccjit}/lib"
    for d in ${libgccjit}/lib/gcc/*/*; do
      [ -d "$d" ] && LIBRARY_PATH="$d:$LIBRARY_PATH"
    done
    ${lib.optionalString (stdenv.hostPlatform.isDarwin && apple-sdk != null) ''
      for d in ${apple-sdk}/Platforms/MacOSX.platform/Developer/SDKs/*.sdk/usr/lib; do
        [ -d "$d" ] && LIBRARY_PATH="$d:$LIBRARY_PATH"
      done
    ''}
    ${lib.optionalString stdenv.hostPlatform.isLinux ''
      LIBRARY_PATH="${
        lib.makeLibraryPath [
          stdenv.cc.cc
          stdenv.cc.libc
        ]
      }:$LIBRARY_PATH"
    ''}
    export LIBRARY_PATH

    mkdir -p "$out/share/emacs/native-lisp"
    ${emacs-core}/bin/emacs --batch -Q -l ${compileEl}

    if [ -z "$(find "$out/share/emacs/native-lisp" -name '*.eln' -print -quit)" ]; then
      echo "native-lisp: no .eln produced — check load-path/LIBRARY_PATH" >&2
      exit 1
    fi
    echo "native-lisp: $(find "$out/share/emacs/native-lisp" -name '*.eln' | wc -l) eln produced"
  ''
