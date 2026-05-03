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
#
byte_compile_batch = files('../meson/byte_compile_batch.py')
list_lisp_files = files('../meson/list_lisp_files.py')
run_loaddefs = files('../meson/run_loaddefs.py')

# ----------------------------------------------------------------------
# loaddefs.el and *-loaddefs.el -- autoload extraction.  Mirrors the
# 'autoloads' target in lisp/Makefile.in:202.  Files land in the
# source tree (lisp/loaddefs.el etc.) because byte-compile and the
# final emacs.pdmp expect them there.
# ----------------------------------------------------------------------
# Directories to scan, mirroring SUBDIRS_ALMOST in
# lisp/Makefile.in:125 (which deliberately excludes obsolete and
# term to avoid corrupting hand-maintained autoload shims).  The
# empty string scans the top-level lisp/ itself, where frameset.el
# and friends live.  Without it, loaddefs.el lacks the
# frameset-filter-alist autoload that tab-bar.el needs at load
# time.
loaddefs_subdirs = [
  '',  # top-level lisp/
  'calc', 'calendar', 'cedet', 'emacs-lisp', 'emulation', 'erc',
  'eshell', 'gnus', 'image', 'international', 'language', 'leim',
  'mail', 'mh-e', 'net', 'nxml', 'org', 'play',
  'progmodes', 'textmodes', 'url', 'use-package', 'vc',
]
loaddefs_stamp = custom_target(
  'loaddefs-stamp',
  output : 'loaddefs.stamp',
  command : [
    py, run_loaddefs,
    '--bootstrap-emacs', bootstrap_emacs.full_path(),
    '--dump-file',       bootstrap_pdmp.full_path(),
    '--source-root',     meson.global_source_root(),
    '--stamp',           '@OUTPUT@',
    '--charscript',      charscript_el.full_path(),
    '--emoji-zwj',       emoji_zwj_el.full_path(),
    '--subdirs',
  ] + loaddefs_subdirs,
  depends : [bootstrap_emacs, bootstrap_pdmp,
             charscript_el, emoji_zwj_el, charsets_stamp],
  build_by_default : false,
)

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
    '--dump-file',       bootstrap_pdmp.full_path(),
    '--source-root',     meson.global_source_root(),
    '--lisp-dir',        meson.global_source_root() / 'lisp',
    '--output-dir',      meson.current_build_dir(),
    '--manifest',        compile_first_manifest,
    '--stamp',           '@OUTPUT@',
    '--charscript',      charscript_el.full_path(),
    '--emoji-zwj',       emoji_zwj_el.full_path(),
  ],
  depends : [
    bootstrap_emacs, bootstrap_pdmp,
    charscript_el, emoji_zwj_el, charsets_stamp,
  ],
  build_by_default : false,
)

# ----------------------------------------------------------------------
# compile-main: every other .el under lisp/.
# ----------------------------------------------------------------------
# Glob every .el under lisp/ at meson configure time so adding /
# removing an .el invalidates the manifest target.  meson has no
# native glob in custom_target, so use run_command.
_all_lisp_files = run_command(
  py, list_lisp_files,
  '--lisp-dir', meson.global_source_root() / 'lisp',
  '--output',   '-',
  check : true,
).stdout().strip().split('\n')
_all_lisp_paths = []
foreach rel : _all_lisp_files
  if rel != ''
    _all_lisp_paths += meson.global_source_root() / 'lisp' / rel
  endif
endforeach

compile_main_manifest = custom_target(
  'compile-main.manifest',
  output : 'compile-main.manifest',
  command : [
    py, list_lisp_files,
    '--lisp-dir', meson.global_source_root() / 'lisp',
    '--output',   '@OUTPUT@',
  ],
  depend_files : _all_lisp_paths,
  # Must enumerate after loaddefs.el is generated, so the manifest
  # picks up loaddefs.el (and theme-loaddefs.el etc.).  Without
  # those byte-compiled, the final pdump errors with
  #   Attempt to autoload rx while preparing to dump
  # because eager macro expansion of `(autoload 'rx ... nil t)` in
  # source-loaded loaddefs.el triggers a load that pdump rejects.
  depends : [loaddefs_stamp],
  # Don't pull this into the default build set: it transitively
  # depends on loaddefs_stamp -> bootstrap-emacs.pdmp, which is
  # only built when explicitly requested (the dump pipeline is
  # known-flaky during the post-cutover migration).
  build_by_default : false,
)

compile_main_elcs = custom_target(
  'compile-main',
  output : 'compile-main.stamp',
  command : [
    py, byte_compile_batch,
    '--bootstrap-emacs', bootstrap_emacs.full_path(),
    '--dump-file',       bootstrap_pdmp.full_path(),
    '--source-root',     meson.global_source_root(),
    '--lisp-dir',        meson.global_source_root() / 'lisp',
    '--output-dir',      meson.current_build_dir(),
    '--manifest',        compile_main_manifest.full_path(),
    '--stamp',           '@OUTPUT@',
    '--charscript',      charscript_el.full_path(),
    '--emoji-zwj',       emoji_zwj_el.full_path(),
  ],
  depends : [
    bootstrap_emacs, bootstrap_pdmp,
    charscript_el, emoji_zwj_el, charsets_stamp,
    compile_first_elcs, compile_main_manifest, loaddefs_stamp,
  ],
  build_by_default : false,
)

# ----------------------------------------------------------------------
# Phase 5 -- native compilation (lisp/Makefile.in:446-449).
# Disabled when libgccjit is absent.  Runs after compile_main_elcs
# so all .elc are present; .eln files land beside their .el sources
# (the autotools default) and are picked up by native-comp on
# emacs startup.
# ----------------------------------------------------------------------
native_compile = files('../meson/native_compile.py')
if libgccjit_dep.found()
  native_lisp_stamp = custom_target(
    'native-lisp-stamp',
    output : 'native-lisp.stamp',
    command : [
      py, native_compile,
      '--emacs',       meson.global_build_root() / 'src/emacs',
      '--source-root', meson.global_source_root(),
      '--lisp-dir',    meson.global_source_root() / 'lisp',
      '--manifest',    compile_main_manifest.full_path(),
      '--stamp',       '@OUTPUT@',
    ],
    depends : [compile_main_elcs, loaddefs_stamp],
    build_by_default : false,
  )
endif

# ----------------------------------------------------------------------
# Final dump.  emacs --batch -l loadup --temacs=pdump produces
# emacs.pdmp.  Lives here rather than in src/meson.build because it
# depends on compile_main_elcs and loaddefs_stamp.  See
# src/Makefile.in:567-573.
# ----------------------------------------------------------------------
run_dump_lisp = files('../meson/run_dump.py')
emacs_pdmp = custom_target(
  'emacs.pdmp',
  output  : 'emacs.pdmp',
  command : [
    py, run_dump_lisp,
    '--bootstrap-emacs', emacs.full_path(),
    '--source-root',     meson.global_source_root(),
    '--output-pdmp',     '@OUTPUT@',
    '--mode',            'pdump',
    '--charscript',      charscript_el.full_path(),
    '--emoji-zwj',       emoji_zwj_el.full_path(),
    '--doc-file',        etc_doc.full_path(),
  ],
  depends : [
    emacs, charscript_el, emoji_zwj_el, charsets_stamp,
    etc_doc, compile_main_elcs, loaddefs_stamp,
  ],
  build_by_default : false,
)
