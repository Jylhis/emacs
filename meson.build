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

# Platform booleans used throughout.
is_darwin = host_machine.system() == 'darwin'
is_linux  = host_machine.system() == 'linux'

# Dynamic library / module suffixes (configure.ac:4370-4390).
if is_darwin
  conf_data.set_quoted('DYNAMIC_LIB_SUFFIX', '.dylib')
  conf_data.set_quoted('DYNAMIC_LIB_SECONDARY_SUFFIX', '.so')
  conf_data.set_quoted('MODULES_SUFFIX', '.dylib')
  conf_data.set_quoted('MODULES_SECONDARY_SUFFIX', '.so')
else
  conf_data.set_quoted('DYNAMIC_LIB_SUFFIX', '.so')
  conf_data.set_quoted('DYNAMIC_LIB_SECONDARY_SUFFIX', '')
  conf_data.set_quoted('MODULES_SUFFIX', '.so')
  # MODULES_SECONDARY_SUFFIX intentionally left undefined on non-Darwin.
endif

# SIGIO-based input (configure.ac:5952-5955).  Both Darwin and
# GNU/Linux support INTERRUPT_INPUT.
if is_darwin or is_linux
  conf_data.set('INTERRUPT_INPUT', 1)
endif

# FIONREAD / SIGIO usability (configure.ac:6230-6277).
# FIONREAD works on both Darwin and Linux.  SIGIO works on Linux and
# Darwin (configure.ac:5952 sets emacs_broken_SIGIO=no for both).
conf_data.set('USABLE_FIONREAD', 1)
if is_darwin or is_linux
  conf_data.set('USABLE_SIGIO', 1)
endif

# File notification backend (configure.ac:3630-3712).
file_notify = get_option('file-notification')
if file_notify == 'auto' or file_notify == 'yes'
  if is_linux and cc.has_header('sys/inotify.h')
    file_notify = 'inotify'
  elif (is_darwin or host_machine.system() == 'freebsd'
        or host_machine.system() == 'dragonfly'
        or host_machine.system() == 'netbsd'
        or host_machine.system() == 'openbsd')
    file_notify = 'kqueue'
  else
    file_notify = 'no'
  endif
endif
if file_notify == 'inotify'
  conf_data.set('USE_FILE_NOTIFY', 1)
  conf_data.set('HAVE_INOTIFY', 1)
elif file_notify == 'kqueue'
  conf_data.set('USE_FILE_NOTIFY', 1)
  conf_data.set('HAVE_KQUEUE', 1)
elif file_notify == 'gfile'
  conf_data.set('USE_FILE_NOTIFY', 1)
  conf_data.set('HAVE_GFILENOTIFY', 1)
endif

# Darwin-specific defines (configure.ac:6187-6191, 6048, 6074,
# 5914, 5808, 6122, 6143).
if is_darwin
  conf_data.set('DARWIN_OS', 1)
  conf_data.set('SIGNALS_VIA_CHARACTERS', 1)
  conf_data.set('TAB3', 'OXTABS')
  conf_data.set('DONT_REOPEN_PTY', 1)
  conf_data.set('GC_SETJMP_WORKS', 1)
endif

# Linux-specific defines (configure.ac:6195-6196).
if is_linux
  conf_data.set('USG', 1)
  conf_data.set('GNU_LINUX', 1)
  conf_data.set('SIGNALS_VIA_CHARACTERS', 1)
endif

# PTYs are available on all supported POSIX systems
# (configure.ac:5808).
conf_data.set('HAVE_PTYS', 1)

# _setjmp / _longjmp probe (configure.ac:6143).
if cc.has_function('_setjmp')
  conf_data.set('HAVE__SETJMP', 1)
endif

# PTY iteration macros (configure.ac:5988-6023).  Both Darwin and
# Linux use Unix98 PTYs with posix_openpt/grantpt.
if cc.has_function('posix_openpt')
  conf_data.set('UNIX98_PTYS', 1)
  conf_data.set('PTY_ITERATION', 'int i; for (i = 0; i < 1; i++)')
  conf_data.set('PTY_OPEN',
    'do { fd = posix_openpt (O_RDWR | O_CLOEXEC | O_NOCTTY);' +
    ' if (fd < 0 && errno == EINVAL)' +
    ' fd = posix_openpt (O_RDWR | O_NOCTTY); } while (false)')
  conf_data.set('PTY_NAME_SPRINTF', '')
  conf_data.set('PTY_TTY_NAME_SPRINTF',
    '{ char *ptyname = 0; sigset_t blocked;' +
    ' sigemptyset (&blocked);' +
    ' sigaddset (&blocked, SIGCHLD);' +
    ' pthread_sigmask (SIG_BLOCK, &blocked, 0);' +
    ' if (grantpt (fd) != -1 && unlockpt (fd) != -1)' +
    ' ptyname = ptsname(fd);' +
    ' pthread_sigmask (SIG_UNBLOCK, &blocked, 0);' +
    ' if (!ptyname) { emacs_close (fd); return -1; }' +
    ' snprintf (pty_name, PTY_NAME_SIZE, "%s", ptyname); }')
elif cc.has_function('getpt')
  conf_data.set('UNIX98_PTYS', 1)
  conf_data.set('PTY_ITERATION', 'int i; for (i = 0; i < 1; i++)')
  conf_data.set('PTY_OPEN', 'fd = getpt ()')
  conf_data.set('PTY_NAME_SPRINTF', '')
  conf_data.set('PTY_TTY_NAME_SPRINTF',
    '{ char *ptyname = 0; sigset_t blocked;' +
    ' sigemptyset (&blocked);' +
    ' sigaddset (&blocked, SIGCHLD);' +
    ' pthread_sigmask (SIG_BLOCK, &blocked, 0);' +
    ' if (grantpt (fd) != -1 && unlockpt (fd) != -1)' +
    ' ptyname = ptsname(fd);' +
    ' pthread_sigmask (SIG_UNBLOCK, &blocked, 0);' +
    ' if (!ptyname) { emacs_close (fd); return -1; }' +
    ' snprintf (pty_name, PTY_NAME_SIZE, "%s", ptyname); }')
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
  'copy_file_range', 'memrchr',
]
  if cc.has_function(fn)
    conf_data.set('HAVE_' + fn.to_upper(), 1)
  endif
endforeach

# Declaration probes for gnulib headers that use HAVE_DECL_*.
if cc.has_header_symbol('string.h', 'strmode')
  conf_data.set('HAVE_DECL_STRMODE', 1)
endif

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
# On macOS, toolkit=auto should NOT require GTK (NS is the native
# window system).  Only require GTK when explicitly requested.
_gtk_required = get_option('toolkit') == 'gtk3'
if get_option('toolkit') == 'auto' and not is_darwin
  _gtk_required = true
endif
gtk3_dep      = dependency('gtk+-3.0',  required : _gtk_required)
# Verify GTK3 X11 backend is usable (gdk/gdkx.h exists).  On macOS,
# Nix may provide GTK3 without X11 backend headers.
if gtk3_dep.found()
  if not cc.has_header('gdk/gdkx.h',
                        dependencies : gtk3_dep)
    if _gtk_required
      error('GTK3 found but gdk/gdkx.h is missing (no X11 backend)')
    endif
    gtk3_dep = dependency('', required : false)
  endif
endif
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
# file ships with libgccjit, so probe for the header.  Try
# platform-specific GCC include paths first, then fall back to the
# default include path (covers Nix, Homebrew, MacPorts).
libgccjit_dep = dependency('', required : false)  # placeholder
if is_linux
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
endif
# Fallback: header in the default include path (Nix, Homebrew, etc.).
if not libgccjit_dep.found() and cc.has_header('libgccjit.h')
  libgccjit_dep = declare_dependency(
    dependencies : cc.find_library('gccjit', required : true),
  )
endif

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
  conf_data.set('HAVE_GLIB', 1)
  # X11 feature probes (configure.ac AC_CHECK_FUNCS block).
  # All true on Linux/X11R7+ and X11 via Nix on macOS.
  conf_data.set('HAVE_XRMSETDATABASE', 1)
  conf_data.set('HAVE_XKB', 1)
  conf_data.set('HAVE_XRENDER', 1)
  conf_data.set('HAVE_XCOMPOSITE', 1)
  conf_data.set('HAVE_XSHAPE', 1)
  conf_data.set('HAVE_XKBGETKEYBOARD', 1)
  conf_data.set('HAVE_XINERAMA', 1)
  conf_data.set('HAVE_XRANDR', 1)
  conf_data.set('HAVE_XFIXES', 1)
  conf_data.set('HAVE_XSYNC', 1)
  conf_data.set('HAVE_XSCREENNUMBEROFSCREEN', 1)
  conf_data.set('HAVE_XSCREENRESOURCESTRING', 1)
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
subdir('admin')    # Phase 6: charsets + unidata generators
subdir('src')      # Phase 3: temacs + bootstrap-emacs
subdir('lisp')     # Phase 4-5: byte-compile + native-comp
subdir('test')     # Phase 7: ERT smoke tests
subdir('doc')      # Phase 6: texinfo info manuals
# subdir('leim')     # Phase 6 (TODO)
# subdir('nextstep') # Phase 8: macOS .app (TODO)
# subdir('java')     # Phase 8: Android cross-build (TODO)

# ----------------------------------------------------------------------
# Phase 9 -- install rules.  Replicates the bare minimum of
# Makefile.in's install targets (lines 552-937).  The full set
# includes desktop / icon / gsettings schema / info / man pages;
# those land as we move them out of comments below.
# ----------------------------------------------------------------------
prefix = get_option('prefix')
datadir = get_option('datadir')          # share/
bindir = get_option('bindir')            # bin/
libexecdir = get_option('libexecdir')    # libexec/
infodir = get_option('infodir')          # share/info/
mandir = get_option('mandir')            # share/man/

emacs_data = datadir / 'emacs' / meson.project_version()
emacs_arch = (libexecdir / 'emacs' / meson.project_version()
              / (host_machine.cpu_family() + '-' + host_machine.system()))

# Install rules driven by meson_install.py.  Custom install script
# is used (instead of install_data on custom_target outputs) because
# install_data evaluates paths at configure time, but our emacs and
# emacs.pdmp don't exist until the build runs.  meson.add_install_script
# runs after the build, by which point the dumped emacs and pdmp
# image are present.
meson.add_install_script(
  py, files('meson/meson_install.py'),
  '--prefix',     prefix,
  '--bindir',     bindir,
  '--datadir',    emacs_data,
  '--libexecdir', emacs_arch,
  '--build-root', meson.global_build_root(),
  '--source-root', meson.global_source_root(),
  '--version',    meson.project_version(),
)
