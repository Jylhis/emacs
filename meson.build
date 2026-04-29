project(
  'emacs',
  'c',
  version : '31.0.50',
  license : 'GPL-3.0-or-later',
  meson_version : '>= 1.3.0',
  default_options : [
    'c_std=gnu2x',
    'warning_level=1',
    'b_ndebug=if-release',
  ],
)

# This Meson build is a work-in-progress migration from the autotools
# build (configure.ac, Makefile.in).  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md for the
# phase plan.  Until that plan reaches Phase 10 cutover, the autotools
# build remains the canonical way to build Emacs; the Meson tree below
# is incomplete and is being landed phase by phase.

cc = meson.get_compiler('c')
py = import('python').find_installation('python3')

# ----------------------------------------------------------------------
# Generate lib/gnulib-common.h from m4/gnulib-common.m4.  This header
# contains the _GL_ATTRIBUTE_* / _Noreturn / _GL_GNUC_PREREQ macro
# block that gnulib-common.m4 contributes to config.h via AH_VERBATIM
# in the autotools build.  Phase 2 lifts the rest of m4/*.m4 into
# native Meson checks.
# ----------------------------------------------------------------------
extract_ah = files('meson/extract_ah_verbatim.py')

# Source m4 files contributing AH_VERBATIM blocks that gnulib headers
# rely on at compile time.  Order matters because some macros depend on
# others; gnulib-common.m4 must come first.
gnulib_verbatim_inputs = files(
  'm4/gnulib-common.m4',
  'm4/extern-inline.m4',
)

gnulib_common_h = custom_target(
  'gnulib-common.h',
  input : gnulib_verbatim_inputs,
  output : 'gnulib-common.h',
  command : [py, extract_ah, '--output', '@OUTPUT@', '@INPUT@'],
)

# ----------------------------------------------------------------------
# Compiler probes used to populate src/config.h.
# ----------------------------------------------------------------------

conf_data = configuration_data()

conf_data.set('PACKAGE_NAME', 'GNU Emacs')
conf_data.set('PACKAGE_VERSION', meson.project_version())
conf_data.set('PACKAGE_STRING', 'GNU Emacs ' + meson.project_version())
conf_data.set('PACKAGE_BUGREPORT', 'bug-gnu-emacs@gnu.org')
conf_data.set('PACKAGE_URL', 'https://www.gnu.org/software/emacs/')
conf_data.set('PACKAGE_TARNAME', 'emacs')

# COPYRIGHT and SEPCHAR are referenced unquoted in C code (e.g.
# ebrowse.c uses SEPCHAR as a char literal).  We pass the inner text
# and let the template add the surrounding quotes/character literal
# delimiters.
conf_data.set('COPYRIGHT',
              'Copyright (C) 2026 Free Software Foundation, Inc.')
if host_machine.system() == 'windows'
  conf_data.set('SEPCHAR', ';')
else
  conf_data.set('SEPCHAR', ':')
endif

# Header presence probes.  TODO(phase-2): grow this to mirror the
# AC_CHECK_HEADERS calls in configure.ac.
foreach hdr : [
  'fcntl.h', 'getopt.h', 'inttypes.h', 'limits.h', 'pwd.h', 'signal.h',
  'stdint.h', 'sys/stat.h', 'sys/types.h', 'unistd.h',
]
  if cc.has_header(hdr)
    conf_data.set('HAVE_' + hdr.to_upper().underscorify(), 1)
  endif
endforeach

# glibc *_unlocked stdio probes consumed by lib/unlocked-io.h.
unlocked_funcs = [
  'clearerr_unlocked', 'feof_unlocked', 'ferror_unlocked',
  'fflush_unlocked', 'fgets_unlocked', 'fileno_unlocked',
  'fputc_unlocked', 'fputs_unlocked', 'fread_unlocked',
  'fwrite_unlocked', 'getc_unlocked', 'getchar_unlocked',
  'putc_unlocked', 'putchar_unlocked',
]
foreach fn : unlocked_funcs
  if cc.has_function(fn,
        prefix : '#define _GNU_SOURCE 1\n#include <stdio.h>')
    conf_data.set('HAVE_DECL_' + fn.to_upper(), 1)
  else
    conf_data.set('HAVE_DECL_' + fn.to_upper(), 0)
  endif
endforeach

# Linux xattr support drives file_has_acl (m4/acl.m4).  Probed here
# rather than in lib/meson.build because the result conditions other
# detection.
have_linux_xattr_h = cc.has_header('linux/xattr.h')
have_listxattr = cc.has_function('listxattr',
                                  prefix : '#include <sys/xattr.h>')
if have_linux_xattr_h
  conf_data.set('HAVE_LINUX_XATTR_H', 1)
endif
if have_listxattr
  conf_data.set('HAVE_LISTXATTR', 1)
endif
# Don't pull in libacl, libselinux, libsmack at this stage: keep
# file_has_acl strictly listxattr-driven on Linux for now.  Phase 2
# follow-ups can wire those when --with-acl support is reintroduced.

# C99 flexible array member support (m4/flexmember.m4).  If the
# compiler accepts `char name[];` as a flexible array, define
# FLEXIBLE_ARRAY_MEMBER to nothing; otherwise to 1 (the struct hack).
flexmember_test = '''
#include <stdlib.h>
#include <stddef.h>
struct m { struct m *next, **list; char name[]; };
struct s { struct s *p; struct m *m; int n; double d[]; };
int main(void) {
  struct s *p = malloc(sizeof(struct s));
  return p ? 0 : 1;
}
'''
if cc.compiles(flexmember_test, name : 'C99 flexible array member')
  conf_data.set('FLEXIBLE_ARRAY_MEMBER', '')
else
  conf_data.set('FLEXIBLE_ARRAY_MEMBER', '1')
endif

config_h = configure_file(
  input : 'meson/config.h.in',
  output : 'config.h',
  configuration : conf_data,
)

# include_directories('.') from the project root resolves to both the
# source tree and the build tree, so subdir Meson files can pick up
# the generated config.h via this dependency.  meson/ is also on the
# include path so config.h can pull in gl-strextras.h.
top_inc = include_directories('.', 'meson')

emacs_version = meson.project_version()

# ----------------------------------------------------------------------
# Subdir wiring.  Each phase fills in another directory.
# ----------------------------------------------------------------------

subdir('lib')      # Phase 2: full gnulib port (currently a stub)
subdir('lib-src')  # Phase 1: helper executables (in progress)
subdir('src')      # Phase 3: globals.h, lisp.mk (compilation TBD)
# subdir('lisp')     # Phase 4-5: byte-compile + native-comp
# subdir('leim')     # Phase 6
# subdir('admin')    # Phase 6: charsets, grammars, unidata
# subdir('doc')      # Phase 6: texinfo manuals
# subdir('test')     # Phase 7: ERT
# subdir('nextstep') # Phase 8: macOS .app
# subdir('java')     # Phase 8: Android cross-build
