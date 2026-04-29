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

# configure.ac:6365 / 6782 -- recorded build flags that emacs prints
# from system-configuration-options / system-configuration-features.
conf_data.set('EMACS_CONFIG_OPTIONS',
              'meson setup --buildtype=debug')
conf_data.set('EMACS_CONFIG_FEATURES',
              'GTK3 CAIRO HARFBUZZ FREETYPE GNUTLS TREE_SITTER ' +
              'SQLITE3 LIBXML2 LIBSYSTEMD GMP')

# Canonical build triple, used by system-configuration variable.
conf_data.set('EMACS_CONFIGURATION',
              host_machine.cpu_family() + '-pc-' + host_machine.system())

# OS family / opsys, used for system-type symbol and a few code paths.
# Mirrors configure.ac:2145.
conf_data.set('SYSTEM_TYPE', host_machine.system())

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
  'sys/resource.h', 'sys/utsname.h', 'sys/select.h', 'sys/socket.h',
  'sys/un.h', 'sys/wait.h', 'sys/time.h', 'sys/ioctl.h', 'sys/mman.h',
  'sys/param.h', 'sys/random.h', 'sys/sysinfo.h', 'sys/file.h',
  'sys/inotify.h', 'sys/eventfd.h', 'sys/timerfd.h', 'sys/syscall.h',
  'sys/prctl.h', 'sys/personality.h', 'sys/sysmacros.h',
  'arpa/inet.h', 'arpa/nameser.h', 'netinet/in.h', 'netinet/tcp.h',
  'net/if.h', 'netdb.h', 'fenv.h', 'pthread.h', 'utime.h', 'utmp.h',
  'wchar.h', 'wctype.h', 'sched.h', 'syslog.h', 'crypt.h',
  'malloc.h', 'malloc/malloc.h', 'mntent.h', 'paths.h',
  'termios.h', 'termio.h', 'sgtty.h', 'grp.h',
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

# Misc POSIX function probes (configure.ac AC_CHECK_FUNCS_ONCE list).
foreach fn : [
  'cfmakeraw', 'cfsetspeed', 'sendto', 'getrandom', 'getentropy',
  'pthread_kill', 'pthread_setname_np', 'getrusage', 'getsockname',
  'gethostname', 'getloadavg', 'utimensat', 'futimens', 'lutimes',
  'pipe2', 'mkostemp', 'mkstemp', 'tcdrain', 'sigsetjmp',
  'eaccess', 'faccessat', 'sysinfo', 'lstat', 'symlink', 'readlink',
  'fchmodat', 'fdopendir', 'sched_setaffinity', 'getpgrp', 'tgkill',
  'gettimeofday', 'getopt_long_only', 'gnu_get_libc_version',
]
  if cc.has_function(fn)
    conf_data.set('HAVE_' + fn.to_upper(), 1)
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

# ----------------------------------------------------------------------
# Window system & feature dependencies (configure.ac EMACS_CHECK_MODULES
# block, lines 2167-4067).  Each one is gated by a meson.options flag
# so --without-feature works.  Phase 3 baseline: Linux/GTK3 only.
# ----------------------------------------------------------------------
gtk3_dep      = dependency('gtk+-3.0',  required : get_option('toolkit') == 'gtk3' or get_option('toolkit') == 'auto')
cairo_dep     = dependency('cairo',     required : get_option('cairo'))
cairo_ft_dep  = dependency('cairo-ft',  required : get_option('cairo'))
harfbuzz_dep  = dependency('harfbuzz',  required : get_option('harfbuzz'))
freetype_dep  = dependency('freetype2', required : false)
fontconfig_dep = dependency('fontconfig', required : false)
xft_dep       = dependency('xft',       required : get_option('xft'))
gnutls_dep    = dependency('gnutls',    required : get_option('gnutls'))
treesit_dep   = dependency('tree-sitter', required : get_option('tree-sitter'))
sqlite_dep    = dependency('sqlite3',   required : get_option('sqlite3'))
xml_dep       = dependency('libxml-2.0', required : get_option('xml2'))
systemd_dep   = dependency('libsystemd', required : get_option('libsystemd'))
gmp_dep       = dependency('gmp',       required : false)
if not gmp_dep.found()
  gmp_dep = cc.find_library('gmp', required : true)
endif

# Native compilation via libgccjit (configure.ac:1588).  No pkg-config
# file ships with libgccjit, so probe for the header directly under
# the GCC private include tree.
libgccjit_dep = dependency('', required : false)  # placeholder
foreach gcc_ver : ['14', '13', '12', '11']
  inc = '/usr/lib/gcc/x86_64-linux-gnu/' + gcc_ver + '/include'
  if cc.has_header('libgccjit.h', args : ['-I' + inc])
    libgccjit_dep = declare_dependency(
      compile_args : ['-I' + inc],
      dependencies : cc.find_library('gccjit', required : true),
    )
    break
  endif
endforeach

# Set the corresponding HAVE_* config.h defines based on what was found.
if gtk3_dep.found()
  conf_data.set('HAVE_GTK3', 1)
  conf_data.set('USE_GTK', 1)
  conf_data.set('HAVE_GTK', 1)
  conf_data.set('HAVE_X_WINDOWS', 1)
  conf_data.set('HAVE_X11', 1)
  conf_data.set('HAVE_WINDOW_SYSTEM', 1)
  conf_data.set('POLL_FOR_INPUT', 1)
  conf_data.set('HAVE_TEXT_CONVERSION', 1)
  conf_data.set_quoted('TERM_HEADER', 'gtkutil.h')
endif
if cairo_dep.found()
  conf_data.set('USE_CAIRO', 1)
  conf_data.set('HAVE_CAIRO', 1)
endif
if harfbuzz_dep.found()
  conf_data.set('HAVE_HARFBUZZ', 1)
endif
if freetype_dep.found()
  conf_data.set('HAVE_FREETYPE', 1)
  conf_data.set('USE_FONT_BACKEND', 1)
endif
if fontconfig_dep.found()
  conf_data.set('HAVE_FONTCONFIG', 1)
endif
if xft_dep.found()
  conf_data.set('HAVE_XFT', 1)
endif
if gnutls_dep.found()
  conf_data.set('HAVE_GNUTLS', 1)
endif
if treesit_dep.found()
  conf_data.set('HAVE_TREE_SITTER', 1)
endif
if sqlite_dep.found()
  conf_data.set('HAVE_SQLITE3', 1)
endif
if xml_dep.found()
  conf_data.set('HAVE_LIBXML2', 1)
endif
if systemd_dep.found()
  conf_data.set('HAVE_LIBSYSTEMD', 1)
endif
conf_data.set('HAVE_GMP', 1)
if libgccjit_dep.found()
  conf_data.set('HAVE_NATIVE_COMP', 1)
endif

# EMACS_INT type and its alignof (configure.ac:2814).  src/lisp.h
# requires both at preprocessor time.
emacs_int_probe = '''
#include <limits.h>
#include <stdint.h>
#if INTPTR_MAX <= INT_MAX && !defined WIDE_EMACS_INT
typedef int emacs_int_type;
#elif INTPTR_MAX <= LONG_MAX && !defined WIDE_EMACS_INT
typedef long int emacs_int_type;
#elif INTPTR_MAX <= LLONG_MAX
typedef long long int emacs_int_type;
#endif
int main(void) { return _Alignof (emacs_int_type); }
'''
emacs_int_align = cc.run(emacs_int_probe,
                          name : 'alignof EMACS_INT').returncode()
conf_data.set('ALIGNOF_EMACS_INT', emacs_int_align)
sizeof_emacs_int = cc.sizeof('long')   # matches the 64-bit Linux choice
conf_data.set('SIZEOF_EMACS_INT', sizeof_emacs_int)

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

subdir('lib')      # Phase 2: full gnulib port (in progress)
subdir('lib-src')  # Phase 1: helper executables (working)
subdir('admin')    # Phase 6: charsets + unidata generators (stopgap)
subdir('src')      # Phase 3: temacs + bootstrap-emacs (working)
subdir('lisp')     # Phase 4: byte-compile (pilot)
# subdir('lisp')     # Phase 4-5: byte-compile + native-comp
# subdir('leim')     # Phase 6
# subdir('admin')    # Phase 6: charsets, grammars, unidata
# subdir('doc')      # Phase 6: texinfo manuals
# subdir('test')     # Phase 7: ERT
# subdir('nextstep') # Phase 8: macOS .app
# subdir('java')     # Phase 8: Android cross-build
