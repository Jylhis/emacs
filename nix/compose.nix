# Directly-runnable full Emacs assembled from the split pieces: the cheap
# emacs-core plus the separately-compiled native-lisp eln tree.
#
# The core binary is wrapped so EMACSNATIVELOADPATH points at native-lisp's
# `share/emacs/native-lisp` (startup.el pushes each entry onto
# `native-comp-eln-load-path`, then comp appends the <abi> subdir).  The result
# behaves like the full-AOT monolith, but core and native-lisp are built and
# cached as independent derivations.
{
  runCommand,
  makeWrapper,
  emacs-core,
  native-lisp,
  version ? "32.0.50",
}:

runCommand "emacs-jylhis-split-${version}"
  {
    nativeBuildInputs = [ makeWrapper ];
    inherit (emacs-core) meta;
    passthru = { inherit emacs-core native-lisp; };
  }
  ''
    mkdir -p $out/bin
    # Wrap every executable from core so the daemon and emacsclient all see the
    # AOT eln; emacs itself is the one that needs EMACSNATIVELOADPATH.
    for exe in ${emacs-core}/bin/*; do
      name=$(basename "$exe")
      makeWrapper "$exe" "$out/bin/$name" \
        --prefix EMACSNATIVELOADPATH : "${native-lisp}/share/emacs/native-lisp"
    done

    # Share the rest of the tree (share/, lib/, …) so data-directory etc. work.
    for d in share lib libexec; do
      [ -e "${emacs-core}/$d" ] && ln -s "${emacs-core}/$d" "$out/$d"
    done
  ''
