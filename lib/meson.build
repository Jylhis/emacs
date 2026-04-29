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
  'c-strcasecmp.c',
  'c-strncasecmp.c',
  'fingerprint.c',
  'memeq.c',
  'sha256.c',
  'streq.c',
  'unistd.c',
)

# ----------------------------------------------------------------------
# *.in.h -> *.h substitution.
#
# gnulib *.in.h files are templates that the autotools build processes
# into real headers using sed (see lib/Makefile.in:107 onward).  We
# replace each one with a Meson configure_file().  Phase 2 brings them
# in as needed; the full set of 28 substitutions lands incrementally.
# ----------------------------------------------------------------------

# stdckdint.h: checked integer arithmetic (C23 / __builtin_add_overflow).
# Required by lib-src/etags.c.
stdckdint_data = configuration_data()
stdckdint_data.set('GUARD_PREFIX', 'GL')
stdckdint_data.set('PRAGMA_SYSTEM_HEADER', '#pragma GCC system_header')
stdckdint_data.set('PRAGMA_COLUMNS', '')
if cc.has_header('stdckdint.h')
  stdckdint_data.set('HAVE_C_STDCKDINT_H', '1')
  stdckdint_data.set('HAVE_WORKING_C_STDCKDINT_H', '1')
  stdckdint_data.set('NEXT_STDCKDINT_H', '<stdckdint.h>')
  stdckdint_data.set('INCLUDE_NEXT', 'include_next')
else
  stdckdint_data.set('HAVE_C_STDCKDINT_H', '0')
  stdckdint_data.set('HAVE_WORKING_C_STDCKDINT_H', '0')
  stdckdint_data.set('NEXT_STDCKDINT_H', '')
  stdckdint_data.set('INCLUDE_NEXT', 'include')
endif
stdckdint_data.set('HAVE_CXX_STDCKDINT_H', '0')
stdckdint_data.set('HAVE_WORKING_CXX_STDCKDINT_H', '0')

stdckdint_h = configure_file(
  input : 'stdckdint.in.h',
  output : 'stdckdint.h',
  configuration : stdckdint_data,
  format : 'cmake@',
)

libgnu = static_library(
  'gnu',
  # The generated gnulib-common.h and *.in.h substitutes are listed as
  # sources so the dependency graph picks them up; they're headers,
  # not TUs, so the compiler skips them.
  sources : [libgnu_sources, gnulib_common_h, stdckdint_h],
  include_directories : [top_inc, include_directories('.', '../src')],
  install : false,
  c_args : ['-DGNULIB_NAMESPACE=gnulib'],
)

libgnu_dep = declare_dependency(
  link_with : libgnu,
  include_directories : [top_inc, include_directories('.')],
  sources : [gnulib_common_h, stdckdint_h],
)
