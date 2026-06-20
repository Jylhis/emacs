# Separate ahead-of-time native-compilation derivation for the core + eln
# split.  `emacs-jylhis-core` AOT-compiles only the preloaded lisp; this
# derivation compiles everything else into its own
# `$out/share/emacs/native-lisp/<abi>/` tree.
#
# nixpkgs' site-start.el appends `<profile>/share/emacs/native-lisp/` to
# `native-comp-eln-load-path` for every entry in NIX_PROFILES, so when this
# package and emacs-jylhis-core are co-installed in a profile the daemon finds
# these .eln and never JIT-compiles them.  The two are cached independently:
# a C change rebuilds only the core; a Lisp change rebuilds only this.
#
# Compiling with the emacs-core binary guarantees the ABI-hash subdirectory
# matches, and `comp-lookup-eln` skips files emacs-core already AOT-compiled so
# the two trees never collide when the profile is built.
{
  runCommand,
  writeText,
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
      ;; First (writable) entry receives new .eln; emacs-core's tree resolves
      ;; dependencies and lets `comp-lookup-eln' detect the preloaded set.
      (setq native-comp-eln-load-path (list out coreeln)
            native-comp-async-report-warnings-errors nil
            warning-minimum-level :error)
      (let ((n 0))
        (dolist (f (directory-files-recursively lispdir "\\.el\\'"))
          (unless (or (comp-lookup-eln f)
                      (string-match-p
                       "/\\(loaddefs\\|ldefs-boot\\|leim-list\\|cus-load\\|finder-inf\\|subdirs\\)\\.el\\'"
                       f))
            (condition-case err
                (progn (native-compile f) (setq n (1+ n)))
              (error (message "skip %s: %S" f err)))))
        (message "native-lisp: compiled %d files" n)))
  '';
in
runCommand "emacs-jylhis-native-lisp-${version}"
  {
    inherit lispDir coreEln;
    meta = {
      description = "AOT native-compiled (.eln) Elisp for emacs-jylhis-core";
      inherit (emacs-core.meta or { }) platforms;
    };
  }
  ''
    mkdir -p "$out/share/emacs/native-lisp"
    ${emacs-core}/bin/emacs --batch -Q -l ${compileEl}

    if [ -z "$(find "$out/share/emacs/native-lisp" -name '*.eln' -print -quit)" ]; then
      echo "native-lisp: no .eln produced — load-path/ABI logic is wrong" >&2
      exit 1
    fi
  ''
