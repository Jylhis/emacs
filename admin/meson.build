# admin/meson.build -- charset and unidata generators.
#
# STATUS: phase 6 in progress.  charsets_stamp now runs natively via
# meson/run_charsets.py (a Python port of admin/charsets/Makefile.in's
# awk pipeline) -- 127 of 131 maps are byte-identical to autotools.
# admin/unidata/Makefile is still invoked as a stopgap for the
# Unicode tables.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md.

# ----------------------------------------------------------------------
# etc/charsets/*.map (~132 files) -- iso8859, BIG5, GB, JIS, etc.
# Native Python port (meson/run_charsets.py) replaces the autotools
# admin/charsets/Makefile dependency.  Output goes to
# $(top_srcdir)/etc/charsets/ so charset map paths in the dumped
# emacs match the autotools build.
# ----------------------------------------------------------------------
run_charsets = files('../meson/run_charsets.py')
charsets_stamp = custom_target(
  'charsets-stamp',
  output : 'charsets.stamp',
  command : [
    py, run_charsets,
    '--charsets-dir', meson.global_source_root() / 'admin/charsets',
    '--out-dir',      meson.global_source_root() / 'etc/charsets',
    '--lispint-dir',  meson.global_source_root() / 'lisp/international',
    '--stamp',        '@OUTPUT@',
  ],
  build_by_default : false,
)

# ----------------------------------------------------------------------
# lisp/international/charscript.el and emoji-zwj.el -- pure awk scripts.
# Easier to port directly than the charset pipeline.
# ----------------------------------------------------------------------
unidir = meson.global_source_root() / 'admin/unidata'
charscript_el = custom_target(
  'charscript.el',
  output : 'charscript.el',
  command : [
    'awk', '-f', unidir / 'blocks.awk',
    unidir / 'Blocks.txt', unidir / 'emoji-data.txt',
  ],
  capture : true,
  build_by_default : false,
)

emoji_zwj_el = custom_target(
  'emoji-zwj.el',
  output : 'emoji-zwj.el',
  command : [
    'awk', '-f', unidir / 'emoji-zwj.awk',
    unidir / 'emoji-zwj-sequences.txt', unidir / 'emoji-sequences.txt',
  ],
  capture : true,
  build_by_default : false,
)
