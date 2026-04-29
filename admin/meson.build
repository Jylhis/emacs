# admin/meson.build -- charset and unidata generators.
#
# STATUS: phase 6 stopgap.  Runs the existing admin/charsets/Makefile
# and admin/unidata/Makefile via `make` rather than porting their
# ~500 lines of awk-based pipelines to native Meson custom_targets.
# That port lands as a follow-up phase-6 commit.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md.
#
# These rules require admin/charsets/Makefile and
# admin/unidata/Makefile to exist, which means autotools'
# ./configure must have been run once.  A future cleanup will
# generate stub Makefiles directly so the autotools dependency goes
# away.

# ----------------------------------------------------------------------
# etc/charsets/*.map (~132 files) -- iso8859, BIG5, GB, JIS, etc.
# Drives admin/charsets/Makefile, which depends on
# admin/charsets/glibc/*.gz and admin/charsets/mapconv (an awk wrapper).
# ----------------------------------------------------------------------
charsets_stamp = custom_target(
  'charsets-stamp',
  output : 'charsets.stamp',
  command : [
    'sh', '-c',
    'cd ' + meson.global_source_root() + '/admin/charsets'
    + ' && make -s charsets.stamp'
    + ' && cp charsets.stamp ' + meson.current_build_dir() + '/charsets.stamp',
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
