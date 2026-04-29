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
  'acl-errno-valid.c',
  'binary-io.c',
  'byteswap.c',
  'c-ctype.c',
  'c-strcasecmp.c',
  'c-strncasecmp.c',
  'file-has-acl.c',
  'fingerprint.c',
  'memeq.c',
  'sha256.c',
  'streq.c',
  'strnul.c',
  'unistd.c',
)

# ----------------------------------------------------------------------
# *.in.h -> *.h substitution.
#
# gnulib *.in.h files are templates that the autotools build processes
# into real headers using sed (see lib/Makefile.in:107 onward).  We
# replace each one with a Meson configure_file().  Phase 2 brings them
# in as needed; the full set of 28 substitutions lands incrementally.
#
# All gnulib in.h files share a small set of standard substitution
# variables.  Build a baseline configuration_data and clone it for
# each header, layering on header-specific overrides.
# ----------------------------------------------------------------------

# Standard variables present in nearly every gnulib in.h file.
in_h_base_set = {
  'PRAGMA_SYSTEM_HEADER': '#pragma GCC system_header',
  'PRAGMA_COLUMNS': '',
  'INCLUDE_NEXT': 'include_next',
  'ASM_SYMBOL_PREFIX': '',
}

# Helper that builds a configuration_data populated with the base
# defaults, overlaid with the per-header dict, then runs configure_file
# on lib/<name>.in.h.
gnulib_substitute_headers = []

# ---- stdckdint.h: checked integer arithmetic (C23). ----
stdckdint_overrides = {
  'GUARD_PREFIX': 'GL',
}
if cc.has_header('stdckdint.h')
  stdckdint_overrides += {
    'HAVE_C_STDCKDINT_H': '1',
    'HAVE_WORKING_C_STDCKDINT_H': '1',
    'NEXT_STDCKDINT_H': '<stdckdint.h>',
  }
else
  stdckdint_overrides += {
    'HAVE_C_STDCKDINT_H': '0',
    'HAVE_WORKING_C_STDCKDINT_H': '0',
    'NEXT_STDCKDINT_H': '',
  }
endif
stdckdint_overrides += {
  'HAVE_CXX_STDCKDINT_H': '0',
  'HAVE_WORKING_CXX_STDCKDINT_H': '0',
}

# ---- assert.h: gnulib's <assert.h> wrapper.  ----
assert_overrides = {
  'NEXT_ASSERT_H': '<assert.h>',
}

# ---- limits.h: extends <limits.h> with extra macros.  ----
limits_overrides = {
  'GUARD_PREFIX': 'GL',
  'NEXT_LIMITS_H': '<limits.h>',
}

# ---- byteswap.h, ieee754.h: no substitutions; just copy.  ----
# These two have zero @VAR@ tokens so configure_file with an empty
# config still works.

# ---- endian.h: byte-order macros.  ----
endian_overrides = {
  'GUARD_PREFIX': 'GL',
}
if cc.has_header('endian.h')
  endian_overrides += {
    'HAVE_ENDIAN_H': '1',
    'HAVE_SYS_ENDIAN_H': '0',
    'NEXT_ENDIAN_H': '<endian.h>',
    'ENDIAN_H_JUST_MISSING_STDINT': '0',
  }
elif cc.has_header('sys/endian.h')
  endian_overrides += {
    'HAVE_ENDIAN_H': '0',
    'HAVE_SYS_ENDIAN_H': '1',
    'NEXT_ENDIAN_H': '',
    'ENDIAN_H_JUST_MISSING_STDINT': '0',
  }
else
  endian_overrides += {
    'HAVE_ENDIAN_H': '0',
    'HAVE_SYS_ENDIAN_H': '0',
    'NEXT_ENDIAN_H': '',
    'ENDIAN_H_JUST_MISSING_STDINT': '0',
  }
endif

# Master list of headers to substitute.  Order doesn't matter; each
# call is independent.
gnulib_in_h_specs = [
  ['stdckdint', stdckdint_overrides],
  ['assert',    assert_overrides],
  ['limits',    limits_overrides],
  ['endian',    endian_overrides],
  ['byteswap',  {}],
  ['ieee754',   {}],
]

gnulib_substituted_headers = []
foreach spec : gnulib_in_h_specs
  name = spec[0]
  overrides = spec[1]
  data = configuration_data()
  foreach k, v : in_h_base_set
    data.set(k, v)
  endforeach
  foreach k, v : overrides
    data.set(k, v)
  endforeach
  out = configure_file(
    input : name + '.in.h',
    output : name + '.h',
    configuration : data,
    format : 'cmake@',
  )
  gnulib_substituted_headers += out
endforeach

# Backward-compatible alias for the first header that used to be a
# named variable.
stdckdint_h = gnulib_substituted_headers[0]

libgnu = static_library(
  'gnu',
  # The generated gnulib-common.h and *.in.h substitutes are listed as
  # sources so the dependency graph picks them up; they're headers,
  # not TUs, so the compiler skips them.
  sources : [libgnu_sources, gnulib_common_h, gnulib_substituted_headers],
  include_directories : [top_inc, include_directories('.', '../src')],
  install : false,
  c_args : ['-DGNULIB_NAMESPACE=gnulib'],
)

libgnu_dep = declare_dependency(
  link_with : libgnu,
  include_directories : [top_inc, include_directories('.')],
  sources : [gnulib_common_h, gnulib_substituted_headers],
)
