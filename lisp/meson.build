# lisp/meson.build -- byte-compile (and eventually native-compile)
# the Emacs Lisp tree.
#
# STATUS: phase 4 starter.  Demonstrates the byte-compile chain by
# compiling a representative batch of .el files through the meson
# build.  A full port covers ~1568 .el files plus loaddefs autoload
# extraction plus the compile-first ordering subtleties in
# lisp/Makefile.in:339.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md.

byte_compile_batch = files('../meson/byte_compile_batch.py')

# Pilot batch.  Mirrors the COMPILE_FIRST list in lisp/Makefile.in:818,
# which the autotools build byte-compiles before the rest.  Each .elc
# lands in build/lisp/<path>.elc.  Phase 4 follow-up replaces this
# with foreach over every .el under lisp/.
compile_first_manifest = configure_file(
  output : 'compile-first.manifest',
  command : ['sh', '-c',
             'cat > $1 <<EOF\n'
             + 'emacs-lisp/debug-early.el\n'
             + 'emacs-lisp/byte-run.el\n'
             + 'emacs-lisp/backquote.el\n'
             + 'subr.el\n'
             + 'keymap.el\n'
             + 'version.el\n'
             + 'widget.el\n'
             + 'custom.el\n'
             + 'emacs-lisp/map-ynp.el\n'
             + 'EOF\n', 'sh', '@OUTPUT@'],
)

compile_first_elcs = custom_target(
  'compile-first',
  output : 'compile-first.stamp',
  command : [
    py, byte_compile_batch,
    '--bootstrap-emacs', bootstrap_emacs.full_path(),
    '--source-root',     meson.global_source_root(),
    '--lisp-dir',        meson.global_source_root() / 'lisp',
    '--output-dir',      meson.current_build_dir(),
    '--manifest',        compile_first_manifest,
    '--stamp',           '@OUTPUT@',
  ],
  depends : [
    bootstrap_emacs, charscript_el, emoji_zwj_el, charsets_stamp,
  ],
  build_by_default : false,
)
