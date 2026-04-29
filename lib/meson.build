# lib/meson.build -- gnulib portability library.
#
# STATUS: Phase 2 in progress.  Currently exposes only a thin libgnu
# providing the symbols make-docfile / make-fingerprint reach for at
# link time.  The rest of gnulib (~96 m4 detection blocks, 28 *.in.h
# header substitutions) lands in subsequent commits.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md.

# Sources currently needed by the simplest lib-src host tools.  This
# list grows as phase 2 progresses.
libgnu_sources = files(
  'binary-io.c',
  'c-ctype.c',
  'fingerprint.c',
  'memeq.c',
  'sha256.c',
  'streq.c',
  'unistd.c',
)

libgnu = static_library(
  'gnu',
  # The generated gnulib-common.h is listed as a source so the
  # dependency graph picks it up; it's a header, not a TU, so the
  # compiler skips it.
  sources : [libgnu_sources, gnulib_common_h],
  include_directories : [top_inc, include_directories('.', '../src')],
  install : false,
  c_args : ['-DGNULIB_NAMESPACE=gnulib'],
)

libgnu_dep = declare_dependency(
  link_with : libgnu,
  include_directories : [top_inc, include_directories('.')],
  sources : gnulib_common_h,
)
