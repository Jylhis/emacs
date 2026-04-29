# lisp/meson.build -- byte-compile (and eventually native-compile)
# the Emacs Lisp tree.
#
# STATUS: phase 4 starter.  Demonstrates the byte-compile chain by
# compiling a small handful of .el files through the meson build.
# A full port covers ~1568 .el files plus loaddefs autoload extraction
# plus the compile-first ordering subtleties in lisp/Makefile.in:339.
# See .claude/plans/migrate-from-current-build-replicated-gadget.md.

byte_compile = files('../meson/byte_compile.py')

# Pilot list: a few small files we know byte-compile cleanly.  Each
# .elc lands in build/lisp/<path>.elc.  Phase 4 follow-up replaces
# this with a foreach over every .el in the tree.
pilot_lisp_sources = [
  'emacs-lisp/byte-run.el',
  'emacs-lisp/backquote.el',
  'emacs-lisp/debug-early.el',
]

pilot_elcs = []
foreach src : pilot_lisp_sources
  pilot_elcs += custom_target(
    src.replace('/', '__') + 'c',
    input  : src,
    output : src.split('/')[-1] + 'c',
    command : [
      py, byte_compile,
      '--bootstrap-emacs', bootstrap_emacs.full_path(),
      '--source-root',     meson.global_source_root(),
      '--input',           '@INPUT@',
      '--output',          '@OUTPUT@',
    ],
    depends : [bootstrap_emacs, charscript_el, emoji_zwj_el, charsets_stamp],
    build_by_default : false,
  )
endforeach
