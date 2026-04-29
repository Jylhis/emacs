# lisp/meson.build -- byte-compile (and eventually native-compile)
# the Emacs Lisp tree.
#
# STATUS: phase 4.  Two byte-compile targets:
#
#   compile-first  -- the small priority list from
#                     lisp/Makefile.in:818-823.  Mirrors what the
#                     autotools build pre-compiles before the rest.
#   compile-main   -- everything else under lisp/, discovered at
#                     meson configure time by
#                     meson/list_lisp_files.py.  ~1560 files.
#
# Both invoke meson/byte_compile_batch.py which wraps a single
# bootstrap-emacs --batch -f batch-byte-compile invocation.
# loaddefs autoload extraction lands as a phase-4 follow-up.
# See .claude/plans/migrate-from-current-build-replicated-gadget.md.

byte_compile_batch = files('../meson/byte_compile_batch.py')
list_lisp_files = files('../meson/list_lisp_files.py')

# ----------------------------------------------------------------------
# compile-first: priority byte-compile list (lisp/Makefile.in:818).
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# compile-main: every other .el under lisp/.
# ----------------------------------------------------------------------
compile_main_manifest = custom_target(
  'compile-main.manifest',
  output : 'compile-main.manifest',
  command : [
    py, list_lisp_files,
    '--lisp-dir', meson.global_source_root() / 'lisp',
    '--output',   '@OUTPUT@',
  ],
)

compile_main_elcs = custom_target(
  'compile-main',
  output : 'compile-main.stamp',
  command : [
    py, byte_compile_batch,
    '--bootstrap-emacs', bootstrap_emacs.full_path(),
    '--source-root',     meson.global_source_root(),
    '--lisp-dir',        meson.global_source_root() / 'lisp',
    '--output-dir',      meson.current_build_dir(),
    '--manifest',        compile_main_manifest.full_path(),
    '--stamp',           '@OUTPUT@',
  ],
  depends : [
    bootstrap_emacs, charscript_el, emoji_zwj_el, charsets_stamp,
    compile_first_elcs, compile_main_manifest,
  ],
  build_by_default : false,
)
