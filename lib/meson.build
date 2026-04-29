# lib/meson.build -- gnulib portability library.
#
# STATUS: stub.  Phase 2 of the migration plan ports every m4/*.m4
# feature check and lib/*.in.h header substitution into native Meson.
# Until that lands, this directory does not build via Meson; the
# canonical build remains lib/Makefile.in driven by autotools.
#
# This stub exposes an empty static library called `libgnu` so that
# lib-src/meson.build can declare a link dependency on it without
# Meson erroring out.  Once Phase 2 lands, replace this file with the
# real implementation.

libgnu_stub = static_library(
  'gnu_stub',
  sources : files('gl-meson-stub.c'),
  install : false,
)

libgnu_dep = declare_dependency(
  link_with : libgnu_stub,
  include_directories : include_directories('.'),
)
