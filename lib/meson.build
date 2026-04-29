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
  'acl-internal.c',
  'allocator.c',
  'binary-io.c',
  'boot-time.c',
  'byteswap.c',
  'c-ctype.c',
  'c-strcasecmp.c',
  'c-strncasecmp.c',
  'careadlinkat.c',
  'close-stream.c',
  'dtoastr.c',
  'dtotimespec.c',
  'file-has-acl.c',
  'filemode.c',
  'filevercmp.c',
  'fingerprint.c',
  'gettime.c',
  'lstat.c',
  'md5.c',
  'md5-stream.c',
  'memeq.c',
  'memmem.c',
  'memset_explicit.c',
  'mini-gmp-gnulib.c',
  'mkostemp.c',
  'mktime.c',
  'nproc.c',
  'nstrftime.c',
  'openat-die.c',
  'openat-proc.c',
  'get-permissions.c',
  'qcopy-acl.c',
  'readlinkat.c',
  'realloc.c',
  'save-cwd.c',
  'set-permissions.c',
  'sha1.c',
  'sha256.c',
  'sha3.c',
  'sha512.c',
  'sig2str.c',
  'stat-time.c',
  'streq.c',
  'strnul.c',
  'tempname.c',
  'timespec.c',
  'u64.c',
  'time_rz.c',
  'timegm.c',
  'timespec-add.c',
  'timespec-sub.c',
  'unistd.c',
  'utimens.c',
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

# ---- errno.h: nominally 5 vars; just wrap the system header.  ----
errno_overrides = {
  'GUARD_PREFIX': 'GL',
  'NEXT_ERRNO_H': '<errno.h>',
}

# ---- stddef.h: defines max_align_t, ptrdiff_t, etc.  ----
stddef_overrides = {
  'GUARD_PREFIX': 'GL',
  'NEXT_STDDEF_H': '<stddef.h>',
}

# ---- sys_types.h: blksize_t, etc.  ----
sys_types_overrides = {
  'GUARD_PREFIX': 'GL',
  'NEXT_SYS_TYPES_H': '<sys/types.h>',
}

# ---- string.h: GNU extensions that gnulib portably provides.
# Enable only the inlines lib/file-has-acl.c, sha256.c, and the
# lib-src tools currently call (streq, memeq, strnul).  Now that
# c++defs.h / arg-nonnull.h / warn-on-use.h are spliced in by
# process_in_h.py, the resulting <string.h> compiles cleanly.  ----
string_overrides = {
  'GUARD_PREFIX':   'GL',
  'NEXT_STRING_H':  '<string.h>',
  'GNULIB_STREQ':   '1',
  'GNULIB_MEMEQ':   '1',
  'GNULIB_STRNUL':  '1',
  'HAVE_DECL_STREQ':  '0',
  'HAVE_DECL_MEMEQ':  '0',
  'HAVE_DECL_STRNUL': '0',
  '_GL_BEGIN_NAMESPACE': '',
  '_GL_END_NAMESPACE':   '',
}

# Master list of headers to substitute.  Order doesn't matter; each
# call is independent.
#
# Only headers added here have been verified to substitute cleanly on
# Linux glibc with default-zero @GNULIB_*@ / @REPLACE_*@ values.  The
# remaining gnulib *.in.h files (string.in.h, stdio.in.h,
# stdlib.in.h, signal.in.h, sys_stat.in.h, time.in.h, unistd.in.h,
# fcntl.in.h, dirent.in.h, getopt.in.h, getopt-cdefs.in.h) need
# per-function feature detection (gl_FUNC_FOO calls in m4/) that
# isn't ported yet.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md.
gnulib_in_h_specs = [
  ['stdckdint', stdckdint_overrides],
  ['assert',    assert_overrides],
  ['limits',    limits_overrides],
  ['endian',    endian_overrides],
  ['byteswap',  {}],
  ['ieee754',   {}],
  ['errno',     errno_overrides],
  ['stddef',    stddef_overrides],
  ['sys_types', sys_types_overrides],
  ['string',    string_overrides],
]

# Process every header through meson/process_in_h.py, which sets any
# unspecified @VAR@ to "0".  This avoids listing 100+ default-zero
# variables for headers like stdlib.in.h, string.in.h, unistd.in.h.
process_in_h = files('../meson/process_in_h.py')

gnulib_substituted_headers = []
foreach spec : gnulib_in_h_specs
  name = spec[0]
  overrides = spec[1]
  set_args = []
  foreach k, v : in_h_base_set
    set_args += ['--set', k + '=' + v]
  endforeach
  foreach k, v : overrides
    set_args += ['--set', k + '=' + v]
  endforeach
  out = custom_target(
    name + '.h',
    input : name + '.in.h',
    output : name + '.h',
    command : [py, process_in_h, '--input', '@INPUT@',
               '--output', '@OUTPUT@',
               '--lib-dir', meson.current_source_dir()] + set_args,
  )
  gnulib_substituted_headers += out
endforeach

libgnu = static_library(
  'gnu',
  # The generated gnulib-common.h and *.in.h substitutes are listed as
  # sources so the dependency graph picks them up; they're headers,
  # not TUs, so the compiler skips them.
  sources : [libgnu_sources, gnulib_common_h, gnulib_substituted_headers],
  include_directories : [top_inc, include_directories('.', '../src')],
  install : false,
  # NEED_MKTIME_INTERNAL exports mktime_internal from mktime.c so
  # time_rz.c can call it at link time (lib/mktime.c:30 + lib/mktime-internal.h).
  c_args : ['-DGNULIB_NAMESPACE=gnulib', '-DNEED_MKTIME_INTERNAL=1'],
)

libgnu_dep = declare_dependency(
  link_with : libgnu,
  include_directories : [top_inc, include_directories('.')],
  sources : [gnulib_common_h, gnulib_substituted_headers],
)
