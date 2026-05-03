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

# Meson + Ninja build for GNU Emacs.  Replaces the autotools build
# (configure.ac, Makefile.in) deleted at the phase-10 cutover; see
# `.claude/notes/build-system.md` for the post-cutover parity audit.

cc = meson.get_compiler('c')
py = import('python').find_installation('python3')

# ----------------------------------------------------------------------
# Generate lib/gnulib-common.h from m4/gnulib-common.m4.  This header
# contains the _GL_ATTRIBUTE_* / _Noreturn / _GL_GNUC_PREREQ macro
# block that gnulib-common.m4 contributed to config.h via AH_VERBATIM
# in the autotools build.
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

# EMACS_CONFIG_OPTIONS / EMACS_CONFIG_FEATURES are filled in below,
# after all dependency probes have run, so that
# system-configuration-options and system-configuration-features
# describe the actual build (configure.ac:6365 / 6782).

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
  'copy_file_range', 'memrchr', 'snprintf', 'sigdescr_np',
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
# Skip the probe entirely for toolkit=none / pgtk so a developer
# host with GTK3 installed doesn't silently flip on HAVE_GTK3.
_toolkit = get_option('toolkit')
_gtk_required = _toolkit == 'gtk3'
if _toolkit == 'auto' and not is_darwin
  _gtk_required = true
endif
if _toolkit == 'gtk3' or (_toolkit == 'auto' and not is_darwin)
  gtk3_dep = dependency('gtk+-3.0', required : _gtk_required)
else
  gtk3_dep = dependency('', required : false)
endif
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
# freetype/fontconfig must be present whenever a window-system
# build is selected (src/meson.build always compiles ftfont.c +
# ftcrfont.c + hbfont.c when gtk3_dep is found).  Forcing them
# required here turns missing-header link errors at compile time
# into a clear meson-setup failure.
_font_required = gtk3_dep.found()
freetype_dep  = dependency('freetype2', required : _font_required)
fontconfig_dep = dependency('fontconfig', required : _font_required)
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

# WIDE_EMACS_INT widens EMACS_INT to 62 bits on 32-bit hosts;
# configure.ac:--with-wide-int.
if get_option('wide-int')
  conf_data.set('WIDE_EMACS_INT', 1)
endif

# Xwidgets pull in WebKitGTK and embed live web views in buffers
# (configure.ac:--with-xwidgets).  Auto/disabled probes for
# webkit2gtk-4.1; the source-tree consumers (src/xwidget.c,
# lisp/xwidget.el) gate on HAVE_XWIDGETS.  GTK3 is the only
# toolkit on this branch that supports it.
xwidgets_opt = get_option('xwidgets')
if xwidgets_opt.allowed() and gtk3_dep.found()
  webkit_dep = dependency('webkit2gtk-4.1', required : xwidgets_opt)
  if webkit_dep.found()
    conf_data.set('HAVE_XWIDGETS', 1)
    conf_data.set('USE_GTK_FOR_XWIDGETS', 1)
  endif
else
  webkit_dep = dependency('', required : false)
endif

# ----------------------------------------------------------------------
# EMACS_CONFIG_OPTIONS / EMACS_CONFIG_FEATURES (configure.ac:6365 / 6782).
#
# Compose strings that mirror what the autotools build embedded, so
# `system-configuration-options` and `system-configuration-features`
# in the dumped Emacs describe the actual build rather than a static
# placeholder.  config.h.in wraps both with `"..."` already, so use
# plain set() not set_quoted().
# ----------------------------------------------------------------------
_opts = ['meson', 'setup', '--buildtype=' + get_option('buildtype'),
         '--prefix=' + get_option('prefix')]
foreach _knob : [
  'all-features', 'native-compilation', 'toolkit', 'pgtk', 'ns',
  'tree-sitter', 'gnutls', 'sqlite3', 'xml2', 'libsystemd',
  'cairo', 'harfbuzz', 'xft', 'jpeg', 'tiff', 'gif', 'png', 'rsvg',
  'webp', 'imagemagick', 'lcms2', 'dbus', 'gsettings', 'gpm',
  'modules', 'threads', 'sound', 'file-notification',
  'gcc-warnings', 'lto', 'check-lisp-object-type',
  'small-ja-dic', 'mailutils', 'pop',
  'wide-int', 'xwidgets', 'compress-install',
]
  _v = get_option(_knob)
  _opts += '-D' + _knob + '=' + '@0@'.format(_v)
endforeach
# `checking` is an array option; format it explicitly.
_opts += '-Dchecking=' + ','.join(get_option('checking'))
conf_data.set('EMACS_CONFIG_OPTIONS', ' '.join(_opts))

_features = []
if gtk3_dep.found()
  _features += 'GTK3'
endif
if conf_data.has('HAVE_X11')
  _features += 'X11'
endif
if cairo_dep.found()
  _features += 'CAIRO'
endif
if harfbuzz_dep.found()
  _features += 'HARFBUZZ'
endif
if freetype_dep.found()
  _features += 'FREETYPE'
endif
if fontconfig_dep.found()
  _features += 'FONTCONFIG'
endif
if xft_dep.found()
  _features += 'XFT'
endif
if gnutls_dep.found()
  _features += 'GNUTLS'
endif
if treesit_dep.found()
  _features += 'TREE_SITTER'
endif
if sqlite_dep.found()
  _features += 'SQLITE3'
endif
if xml_dep.found()
  _features += 'LIBXML2'
endif
if systemd_dep.found()
  _features += 'LIBSYSTEMD'
endif
if libgccjit_dep.found()
  _features += 'NATIVE_COMP'
endif
_features += 'GMP'
conf_data.set('EMACS_CONFIG_FEATURES', ' '.join(_features))

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
# Standard install path variables.  These need to be defined before the
# subdirs so per-subdir install_dir arguments resolve correctly.
# ----------------------------------------------------------------------
prefix             = get_option('prefix')
datadir            = get_option('datadir')           # share/
bindir             = get_option('bindir')            # bin/
libexecdir         = get_option('libexecdir')        # libexec/
infodir            = get_option('infodir')           # share/info/
mandir             = get_option('mandir')            # share/man/
includedir         = get_option('includedir')        # include/
sysconfdir         = get_option('sysconfdir')        # etc/
localstatedir      = get_option('localstatedir')     # var/
datadirs           = datadir
desktopdir         = datadir / 'applications'
metainfodir        = datadir / 'metainfo'
icondir            = datadir / 'icons'
gsettingsschemadir = datadir / 'glib-2.0' / 'schemas'
systemduserunitdir = get_option('systemduserunitdir')

emacs_data = datadir / 'emacs' / emacs_version
emacs_arch = (libexecdir / 'emacs' / emacs_version
              / (host_machine.cpu_family() + '-' + host_machine.system()))
nativecompdir = emacs_data / 'native-lisp'
emacs_lispdir = emacs_data / 'lisp'
emacs_etcdir  = emacs_data / 'etc'
emacs_docdir  = emacs_arch / 'etc'           # PATH_DOC -> libexec/.../etc

# ----------------------------------------------------------------------
# Subdir wiring.
# ----------------------------------------------------------------------

subdir('lib')      # gnulib portability subset
subdir('lib-src')  # helper executables (etags, emacsclient, ...)
subdir('admin')    # charsets + unidata generators
subdir('src')      # temacs + bootstrap-emacs + emacs binary + DOC
subdir('lisp')     # byte-compile + native-comp + emacs.pdmp
subdir('test')     # ERT test discovery
subdir('doc')      # texinfo info manuals
# subdir('leim')     # TODO: MISC-DIC and friends
# subdir('nextstep') # TODO: macOS .app bundle
# subdir('java')     # TODO: Android cross-build

# ----------------------------------------------------------------------
# Install rules.  Items that exist as static source-tree files use
# meson's native install_data / install_man.  Items that depend on
# build-tree artefacts (etc/DOC, native-lisp/, subdirs.el) are handled
# by meson/meson_install.py via add_install_script (runs after the
# build, when those artefacts exist).  Reference: Makefile.in:552-937.
# ----------------------------------------------------------------------

# Desktop entries (Makefile.in:756-789).  Installed verbatim.  The
# autotools build sed-rewrites Exec= and Icon= lines to honour
# program-transform-name and an Emacs-specific bindir prefix; we
# defer that until --program-suffix lands in meson.options.
install_data(
  'etc/emacs.desktop',
  'etc/emacsclient.desktop',
  'etc/emacs-mail.desktop',
  'etc/emacsclient-mail.desktop',
  install_dir : desktopdir,
)

# AppStream metadata (Makefile.in:791-797).
install_data('etc/emacs.metainfo.xml', install_dir : metainfodir)

# Icons.  Makefile.in:802-820 enumerates `*/*/apps */*/mimetypes`
# under `etc/images/icons/hicolor/` and installs every file matching
# the shell glob `emacs[.-]*` (literal `emacs` + one '.' or '-' +
# suffix).  `emacs.png` and `emacs-document.svg` match;
# `emacs22.png`/`emacs23.png` do not.
#
# Enumerate at configure time via meson/list_icons.py so we don't
# hard-code a list of sizes / kinds and silently drop new icons that
# land in etc/images/icons/hicolor/ later.
icon_lines = run_command(
  py, files('meson/list_icons.py'),
  '--root', meson.global_source_root() / 'etc/images/icons/hicolor',
  check : true,
).stdout().strip().split('\n')
foreach line : icon_lines
  if line != ''
    parts = line.split('\t')
    install_data(parts[0], install_dir : icondir / 'hicolor' / parts[1])
  endif
endforeach

# Manpages (Makefile.in:743-754).  doc/man/ ships static .1 files for
# etags, emacsclient, ebrowse, and a `.1.in` template for emacs.1
# (substitutes @version@ + @PACKAGE_BUGREPORT@).  ChangeLog.1 is
# skipped by the autotools loop.  ctags.1 / hexl.1 do not exist as
# autotools artefacts, so they aren't installed.
emacs_man_data = configuration_data()
emacs_man_data.set('version', emacs_version)
emacs_man_data.set('PACKAGE_BUGREPORT', 'bug-gnu-emacs@gnu.org')
emacs_man = configure_file(
  input : 'doc/man/emacs.1.in',
  output : 'emacs.1',
  configuration : emacs_man_data,
)
install_man(
  emacs_man,
  'doc/man/etags.1',
  'doc/man/emacsclient.1',
  'doc/man/ebrowse.1',
)

# systemd user unit (Makefile.in:798-806).  Only installed if the
# user passed --systemduserunitdir=DIR.
if systemduserunitdir != ''
  install_data('etc/emacs.service', install_dir : systemduserunitdir)
endif

# Per-build artefacts (etc/DOC, native-lisp/, subdirs.el creation,
# emacs/emacs.pdmp from build tree, gameuser sgid bit).  These need
# the build outputs to exist on disk, so they run from the post-build
# install script.
_install_args = [
  '--prefix',           prefix,
  '--bindir',           bindir,
  '--datadir',          emacs_data,
  '--libexecdir',       emacs_arch,
  '--mandir',           mandir,
  '--infodir',          infodir,
  '--build-root',       meson.global_build_root(),
  '--source-root',      meson.global_source_root(),
  '--version',          emacs_version,
  '--gameuser',         get_option('gameuser'),
  '--update-subdirs',
  meson.global_source_root() / 'build-aux' / 'update-subdirs',
]
if get_option('compress-install')
  _install_args += '--compress-install'
endif
meson.add_install_script(
  py, files('meson/meson_install.py'), _install_args,
)
