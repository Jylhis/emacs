# lib/meson.build -- gnulib portability library.
#
# Exposes a thin libgnu covering the symbols make-docfile /
# make-fingerprint and the rest of src reach for at link time.  The
# remaining gnulib detection (m4/* feature probes, *.in.h header
# substitutions) lands incrementally as more emacs sources rely on
# each piece.

# Sources currently needed for the lib-src host tools and emacs.
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
  'copy-file-range.c',
  'dtoastr.c',
  'dtotimespec.c',
  'file-has-acl.c',
  'filemode.c',
  'filevercmp.c',
  'fingerprint.c',
  'free.c',
  'getopt.c',
  'getopt1.c',
  'gettime.c',
  'lstat.c',
  'md5.c',
  'md5-stream.c',
  'memeq.c',
  'memmem.c',
  'mempcpy.c',
  'memrchr.c',
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

# Gnulib replacement sources for functions the system may lack.
# These mirror the conditional logic in lib/gnulib.mk.in.
if not cc.has_function('pipe2')
  libgnu_sources += files('pipe2.c')
endif
if not cc.has_function('sigdescr_np',
    prefix : '#define _GNU_SOURCE 1\n#include <string.h>')
  libgnu_sources += files('sigdescr_np.c')
endif
if not cc.has_function('getrandom',
    prefix : '#include <sys/random.h>')
  libgnu_sources += files('getrandom.c')
endif
if not cc.has_function('__fpending',
    prefix : '#include <stdio_ext.h>')
  libgnu_sources += files('fpending.c')
endif
# regex.c and malloc/dynarray_*.c: gnulib's included POSIX regex
# engine.  lib-src/etags.c uses the GNU regex API (re_compile_pattern,
# re_search, re_match).  On glibc these are provided by the system;
# on other systems (macOS, musl) we need gnulib's implementation.
# The autotools build probes via m4/regex.m4; here we check for the
# GNU extension re_compile_pattern which etags requires.
use_included_regex = not cc.has_function('re_compile_pattern',
  prefix : '#include <regex.h>')
if use_included_regex
  libgnu_sources += files(
    'malloc/dynarray_at_failure.c',
    'malloc/dynarray_emplace_enlarge.c',
    'malloc/dynarray_finalize.c',
    'malloc/dynarray_resize.c',
    'malloc/dynarray_resize_clear.c',
    'regex.c',
  )
endif

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
  'HAVE_BLKSIZE_T': cc.has_type('blksize_t', prefix : '#include <sys/types.h>') ? '1' : '0',
  'HAVE_BLKCNT_T': cc.has_type('blkcnt_t', prefix : '#include <sys/types.h>') ? '1' : '0',
}

# ---- string.h: GNU extensions that gnulib portably provides.
# Enable only the inlines lib/file-has-acl.c, sha256.c, and the
# lib-src tools currently call (streq, memeq, strnul, mempcpy).
# c++defs.h / arg-nonnull.h / warn-on-use.h are spliced in by
# process_in_h.py, so the resulting <string.h> compiles cleanly.  ----
have_mempcpy = cc.has_function('mempcpy',
  prefix : '#define _GNU_SOURCE 1\n#include <string.h>')
have_sigdescr_np = cc.has_function('sigdescr_np',
  prefix : '#define _GNU_SOURCE 1\n#include <string.h>')
string_overrides = {
  'GUARD_PREFIX':   'GL',
  'NEXT_STRING_H':  '<string.h>',
  'GNULIB_STREQ':   '1',
  'GNULIB_MEMEQ':   '1',
  'GNULIB_STRNUL':  '1',
  'GNULIB_MEMPCPY': '1',
  'GNULIB_MEMRCHR': '1',
  'GNULIB_MEMSET_EXPLICIT': '1',
  'GNULIB_SIGDESCR_NP': '1',
  'HAVE_DECL_STREQ':  '0',
  'HAVE_DECL_MEMEQ':  '0',
  'HAVE_DECL_STRNUL': '0',
  'HAVE_MEMPCPY':   have_mempcpy ? '1' : '0',
  'HAVE_DECL_MEMRCHR': cc.has_header_symbol('string.h', 'memrchr') ? '1' : '0',
  'HAVE_MEMSET_EXPLICIT': cc.has_function('memset_explicit') ? '1' : '0',
  'HAVE_SIGDESCR_NP': have_sigdescr_np ? '1' : '0',
  '_GL_BEGIN_NAMESPACE': '',
  '_GL_END_NAMESPACE':   '',
}

# ---- getopt-cdefs.h: compiler introspection for getopt.  ----
getopt_cdefs_overrides = {
  'HAVE_SYS_CDEFS_H': cc.has_header('sys/cdefs.h') ? '1' : '0',
}

# ---- getopt.h: gnulib getopt wrapper (m4/getopt.m4).  ----
# With __GETOPT_PREFIX=rpl_ in config.h, gnulib renames getopt_long
# to rpl_getopt_long etc., avoiding type clashes with macOS SDK.
getopt_overrides = {
  'GUARD_PREFIX':  'GL',
  'HAVE_GETOPT_H': cc.has_header('getopt.h') ? '1' : '0',
  'NEXT_GETOPT_H': '<getopt.h>',
}

# ---- stdlib.h: gnulib <stdlib.h> wrapper.  ----
# Substituted so that meson-generated build/lib/stdlib.h shadows any
# stale autotools-generated lib/stdlib.h left over from a previous
# ./configure && make run.  With default-zero @VAR@, the wrapper just
# include_next's the system <stdlib.h> and adds nothing.
stdlib_overrides = {
  'GUARD_PREFIX':  'GL',
  'NEXT_STDLIB_H': '<stdlib.h>',
}

# ---- time.h: gnulib <time.h> wrapper.  ----
# GNULIB_TIME_RZ enables mktime_z / localtime_rz / tzalloc / tzfree
# declarations needed by lib/time_rz.c and lib/nstrftime.c (via
# strftime.c).  HAVE_TIMEZONE_T is set because config.h.in typedefs
# timezone_t (phase-2 stopgap; eventually time.in.h substitution
# replaces the typedef).
time_overrides = {
  'GUARD_PREFIX':  'GL',
  'NEXT_TIME_H':   '<time.h>',
  'GNULIB_TIME_RZ': '1',
  'HAVE_TIMEZONE_T': '1',
  'GNULIB_MKTIME':  '1',
  'GNULIB_TIMEGM':  '1',
  'GNULIB_TIME_R':  '1',
  'PTHREAD_H_DEFINES_STRUCT_TIMESPEC': '1',
}

# Master list of headers to substitute.  Order doesn't matter; each
# call is independent.
#
# Headers added here have been verified to substitute cleanly with
# default-zero @GNULIB_*@ / @REPLACE_*@ values on Linux glibc and
# macOS.  The remaining gnulib *.in.h files (stdio.in.h,
# signal.in.h, sys_stat.in.h, time.in.h, unistd.in.h, fcntl.in.h,
# dirent.in.h) need per-function feature detection (gl_FUNC_FOO
# calls in m4/) that isn't ported yet.
gnulib_in_h_specs = [
  ['stdckdint',    stdckdint_overrides],
  ['assert',       assert_overrides],
  ['limits',       limits_overrides],
  ['endian',       endian_overrides],
  ['byteswap',     {}],
  ['ieee754',      {}],
  ['errno',        errno_overrides],
  ['stddef',       stddef_overrides],
  ['sys_types',    sys_types_overrides, 'sys/types.h'],
  ['string',       string_overrides],
  ['getopt-cdefs', getopt_cdefs_overrides],
  ['getopt',       getopt_overrides],
  ['stdlib',       stdlib_overrides],
  ['time',         time_overrides],
  ['stdbit',       {
    'GL_STDC_BIT_CEIL': '1',
    'GL_STDC_BIT_FLOOR': '1',
    'GL_STDC_BIT_WIDTH': '1',
    'GL_STDC_COUNT_ONES': '1',
    'GL_STDC_COUNT_ZEROS': '1',
    'GL_STDC_FIRST_LEADING_ONE': '1',
    'GL_STDC_FIRST_LEADING_ZERO': '1',
    'GL_STDC_FIRST_TRAILING_ONE': '1',
    'GL_STDC_FIRST_TRAILING_ZERO': '1',
    'GL_STDC_HAS_SINGLE_BIT': '1',
    'GL_STDC_LEADING_ONES': '1',
    'GL_STDC_LEADING_ZEROS': '1',
    'GL_STDC_TRAILING_ONES': '1',
    'GL_STDC_TRAILING_ZEROS': '1',
  }],
  ['signal',       {
    'GUARD_PREFIX': 'GL',
    'NEXT_SIGNAL_H': '<signal.h>',
    'GNULIB_SIG2STR': '1',
    'HAVE_SIG2STR': cc.has_function('sig2str') ? '1' : '0',
    'HAVE_STR2SIG': cc.has_function('str2sig') ? '1' : '0',
    'HAVE_POSIX_SIGNALBLOCKING': '1',
    'HAVE_SIGSET_T': '1',
    'HAVE_SIGACTION': '1',
    'HAVE_SIGINFO_T': '1',
    'HAVE_RAISE': '1',
    'HAVE_PTHREAD_SIGMASK': '1',
    'HAVE_TYPE_VOLATILE_SIG_ATOMIC_T': '1',
    'HAVE_STRUCT_SIGACTION_SA_SIGACTION': '1',
    'HAVE_SIGHANDLER_T': '1',
  }],
  ['stdint',       {
    'GUARD_PREFIX': 'GL',
    'NEXT_STDINT_H': '<stdint.h>',
    'HAVE_STDINT_H': '1',
    'HAVE_C99_STDINT_H': '1',
    'HAVE_INTTYPES_H': '1',
    'HAVE_SYS_TYPES_H': '1',
    'HAVE_WCHAR_H': '1',
    'APPLE_UNIVERSAL_BUILD': '0',
    'BITSIZEOF_PTRDIFF_T': '64',
    'BITSIZEOF_SIG_ATOMIC_T': '32',
    'BITSIZEOF_SIZE_T': '64',
    'BITSIZEOF_WCHAR_T': '32',
    'BITSIZEOF_WINT_T': '32',
    'PTRDIFF_T_SUFFIX': 'l',
    'SIG_ATOMIC_T_SUFFIX': '',
    'SIZE_T_SUFFIX': 'ul',
    'WCHAR_T_SUFFIX': '',
    'WINT_T_SUFFIX': '',
  }],
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
  out_name = spec.length() > 2 ? spec[2] : name + '.h'
  out = custom_target(
    out_name,
    input : name + '.in.h',
    output : out_name,
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
