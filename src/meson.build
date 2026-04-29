# src/meson.build -- core Emacs C sources.
#
# STATUS: phase 3 in progress.  Currently wires the generators that
# produce src/globals.h and src/lisp.mk -- two artefacts that every
# src/ object file (and the eventual temacs link) depends on.
# Compilation of src/*.c, the temacs/emacs/pdumper bootstrap dance,
# native compilation, and dumping all land in subsequent commits.
# See .claude/plans/migrate-from-current-build-replicated-gadget.md.

# ----------------------------------------------------------------------
# base_obj source list (Linux/GTK3, no NS, no Android baseline).
# Mirrors src/Makefile.in:389-408.  Phase 3 follow-ups will extend
# this with the platform-conditional groups (XOBJ, GTK_OBJ, NS_OBJ,
# ANDROID_OBJ, etc.) once their feature flags are ported.
# ----------------------------------------------------------------------
base_obj_basenames = [
  'alloc.c', 'atimer.c', 'bidi.c', 'bignum.c', 'buffer.c', 'bytecode.c',
  'callint.c', 'callproc.c', 'casefiddle.c', 'casetab.c', 'category.c',
  'ccl.c', 'character.c', 'charset.c', 'chartab.c', 'cmds.c', 'coding.c',
  'composite.c', 'comp.c', 'data.c', 'decompress.c', 'dired.c',
  'dispnew.c', 'doc.c', 'doprnt.c', 'editfns.c', 'emacs.c', 'eval.c',
  'fileio.c', 'filelock.c', 'floatfns.c', 'fns.c', 'font.c', 'frame.c',
  'gnutls.c', 'indent.c', 'insdel.c', 'intervals.c', 'itree.c', 'json.c',
  'keyboard.c', 'keymap.c', 'lcms.c', 'lread.c', 'macros.c', 'marker.c',
  'menu.c', 'minibuf.c', 'pdumper.c', 'print.c', 'process.c',
  'profiler.c', 'regex-emacs.c', 'region-cache.c', 'scroll.c',
  'search.c', 'sort.c', 'sound.c', 'sqlite.c', 'syntax.c', 'sysdep.c',
  'systhread.c', 'term.c', 'terminal.c', 'textprop.c', 'thread.c',
  'timefns.c', 'treesit.c', 'undo.c', 'window.c', 'xdisp.c', 'xfaces.c',
  'xml.c',
]
base_obj_sources = files(base_obj_basenames)

# ----------------------------------------------------------------------
# globals.h -- function/variable forward declarations harvested from
# every src/*.c file by make-docfile -g.  See src/Makefile.in:600.
# ----------------------------------------------------------------------
globals_h = custom_target(
  'globals.h',
  input  : base_obj_sources,
  output : 'globals.h',
  command : [
    make_docfile,
    '-d', meson.current_source_dir(),
    '-g',
  ] + base_obj_basenames,
  capture : true,
)

# ----------------------------------------------------------------------
# lisp.mk -- list of Lisp files loadup.el will load, extracted from
# the (load "...") forms in lisp/loadup.el.  See
# src/Makefile.in:488-494.  We only need this as a Meson-side data
# structure, not a literal makefile fragment, so the script outputs a
# JSON list that meson.build can read once we wire the lisp/ subdir.
# ----------------------------------------------------------------------
make_lisp_mk = files('../meson/make_lisp_mk.py')

shortlisp_json = custom_target(
  'shortlisp.json',
  input   : '../lisp/loadup.el',
  output  : 'shortlisp.json',
  command : [py, make_lisp_mk, '@INPUT@', '@OUTPUT@'],
)

# TODO(phase-3): compile base_obj_sources into temacs.o objects, link
# temacs, run loadup.el via temacs --temacs=pbootstrap to produce
# bootstrap-emacs.pdmp, then re-run as --temacs=pdump for the final
# emacs binary.  See src/Makefile.in:563-895.
