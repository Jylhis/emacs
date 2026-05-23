project(
  'emacs',
  ['c', 'objc'],
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
  elif is_darwin
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

# Linux xattr support drives file_has_acl (gnulib's acl.m4 upstream).
# Probed here rather than in lib/meson.build because the result
# conditions other detection.
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
# Mirrors autotools' --without-all: when the all-features option is
# false, every OPTION_DEFAULT_IFAVAILABLE feature flips from auto to
# disabled (configure.ac:295 at anchor 08a22b8965ec).  Meson's
# feature.disable_auto_if() is the matching primitive; chained on
# every get_option('NAME') below for the relevant features.
all_features = get_option('all-features')
_no_all = not all_features

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

# ----------------------------------------------------------------------
# macOS Cocoa (NextStep) detection.  Auto on darwin, opt-out via
# -Dns=disabled or -Dtoolkit=none.  Mirrors configure.ac's NS_OBJC_OBJ
# block at anchor 08a22b8965ec.  On NS, src/nsterm.m + nsfns.m +
# nsmenu.m + nsselect.m + nsimage.m + macfont.m replace the X11 +
# GTK toolkit sources; framework linkage uses Meson's appleframeworks
# dependency for Cocoa, AppKit, and (for xwidgets) WebKit.
# ----------------------------------------------------------------------
ns_opt = get_option('ns')
ns_dep = dependency('', required : false)
if (is_darwin and ns_opt.allowed()
    and not gtk3_dep.found()
    and _toolkit != 'none')
  # nsterm.m + macfont.m + nsfns.m pull in symbols from these
  # frameworks: Cocoa/AppKit (NS classes), QuartzCore (CALayer),
  # IOSurface (offscreen GPU buffers), Carbon (TIS keyboard
  # layout APIs), CoreText (font rendering), UniformTypeIdentifiers
  # (UTType, macOS 11+).
  ns_dep = dependency('appleframeworks',
                       modules : ['Cocoa', 'AppKit',
                                  'QuartzCore', 'IOSurface',
                                  'Carbon', 'CoreText',
                                  'UniformTypeIdentifiers'],
                       required : ns_opt)
  if ns_dep.found()
    conf_data.set('HAVE_NS', 1)
    conf_data.set('NS_IMPL_COCOA', 1)
    conf_data.set('HAVE_WINDOW_SYSTEM', 1)
    conf_data.set('HAVE_TEXT_CONVERSION', 1)
    conf_data.set_quoted('TERM_HEADER', 'nsterm.h')
  endif
endif
cairo_opt = get_option('cairo').disable_auto_if(_no_all)
cairo_dep     = dependency('cairo',     required : cairo_opt)
cairo_ft_dep  = dependency('cairo-ft',  required : cairo_opt)
harfbuzz_dep  = dependency('harfbuzz',
                            required : get_option('harfbuzz').disable_auto_if(_no_all))
# freetype/fontconfig must be present whenever a window-system
# build is selected (src/meson.build always compiles ftfont.c +
# ftcrfont.c + hbfont.c when gtk3_dep is found).  Forcing them
# required here turns missing-header link errors at compile time
# into a clear meson-setup failure.
_font_required = gtk3_dep.found()
freetype_dep  = dependency('freetype2', required : _font_required)
fontconfig_dep = dependency('fontconfig', required : _font_required)
xft_dep       = dependency('xft',
                            required : get_option('xft').disable_auto_if(_no_all))
gnutls_dep    = dependency('gnutls',    required : get_option('gnutls'))
treesit_dep   = dependency('tree-sitter',
                            required : get_option('tree-sitter').disable_auto_if(_no_all))
sqlite_dep    = dependency('sqlite3',
                            required : get_option('sqlite3').disable_auto_if(_no_all))
xml_dep       = dependency('libxml-2.0',
                            required : get_option('xml2').disable_auto_if(_no_all))
systemd_dep   = dependency('libsystemd',
                            required : get_option('libsystemd').disable_auto_if(_no_all))
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
  # HAVE_X_I18N is unconditional for X11R6+ in autotools (configure.ac
  # XLIB AC_DEFINE block); xterm.c's GTK + XInput2 path expects it.
  # HAVE_X11R6 is the umbrella; xterm.c gates xim_destroy_callback's
  # definition under HAVE_X11R6 && HAVE_X11R6_XIM but the caller only
  # under HAVE_X11R6_XIM, so both must be set together or the symbol
  # is referenced without a definition.
  conf_data.set('HAVE_X_I18N', 1)
  conf_data.set('HAVE_X11R6', 1)
  conf_data.set('HAVE_X11R6_XIM', 1)
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
if cairo_dep.found() and not conf_data.has('HAVE_NS')
  # Cairo is X11-only in the autotools gate (configure.ac:HAVE_X11
  # check at anchor 08a22b8965ec).  macOS Cocoa uses CoreGraphics
  # directly, and dispextern.h's USE_CAIRO branch conflicts with
  # nsgui.h's typedefs.
  conf_data.set('USE_CAIRO', 1)
  conf_data.set('HAVE_CAIRO', 1)
endif
if harfbuzz_dep.found()
  conf_data.set('HAVE_HARFBUZZ', 1)
endif
if freetype_dep.found() and not conf_data.has('HAVE_NS')
  # Autotools at anchor 08a22b8965ec only sets HAVE_FREETYPE inside
  # the HAVE_X11 / pgtk blocks; under NS, font.c's HAVE_FREETYPE
  # branch references freetype symbols that aren't linked because
  # ftfont.c isn't compiled.  macfont.m is the NS font backend.
  conf_data.set('HAVE_FREETYPE', 1)
endif
if freetype_dep.found() or conf_data.has('HAVE_NS')
  # USE_FONT_BACKEND is set whenever a window system is in use; both
  # the X freetype path and macfont.m use the new backend protocol.
  conf_data.set('USE_FONT_BACKEND', 1)
endif
if fontconfig_dep.found() and not conf_data.has('HAVE_NS')
  conf_data.set('HAVE_FONTCONFIG', 1)
endif
if xft_dep.found() and not conf_data.has('USE_CAIRO')
  # xsettings.c at xsettings.c:57-62 selects between
  # `#ifdef USE_CAIRO` (include fontconfig.h + ftfont.h) and
  # `#elif defined HAVE_XFT` (include Xft.h), making the two
  # mutually exclusive.  Later in the same file (e.g. line 988)
  # `#ifdef HAVE_XFT` is used as a standalone gate to call
  # XftDefaultSet, which is only declared by Xft.h.  So if HAVE_XFT
  # is set alongside USE_CAIRO, Xft.h is never included but the
  # call is compiled, leading to "implicit declaration of
  # XftDefaultSet".  Autotools made these mutually exclusive; match
  # that here so the source stays consistent with both build
  # systems.
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
elif xwidgets_opt.enabled()
  error('xwidgets=enabled but GTK3 toolkit is not in use')
else
  webkit_dep = dependency('', required : false)
endif

# ----------------------------------------------------------------------
# Image libraries.  Mapped from EMACS_CHECK_MODULES blocks in
# configure.ac (lines 537-562).  Each is autodetected unless the
# user passes -D<feature>={enabled,disabled}.  Autotools' libungif
# fallback for gif is satisfied by the same pkg-config name on
# Debian/Ubuntu; bare find_library is the fallback.
# ----------------------------------------------------------------------
jpeg_opt = get_option('jpeg').disable_auto_if(_no_all)
jpeg_dep = dependency('libjpeg', required : jpeg_opt)
if not jpeg_dep.found() and jpeg_opt.allowed()
  jpeg_dep = cc.find_library('jpeg', required : jpeg_opt)
endif
if jpeg_dep.found()
  conf_data.set('HAVE_JPEG', 1)
endif

tiff_opt = get_option('tiff').disable_auto_if(_no_all)
tiff_dep = dependency('libtiff-4', required : tiff_opt)
if not tiff_dep.found() and tiff_opt.allowed()
  tiff_dep = cc.find_library('tiff', required : tiff_opt)
endif
if tiff_dep.found()
  conf_data.set('HAVE_TIFF', 1)
endif

png_dep = dependency('libpng',
                      required : get_option('png').disable_auto_if(_no_all))
if png_dep.found()
  conf_data.set('HAVE_PNG', 1)
endif

# giflib historically published `libungif` as its pkg-config name;
# modern distros ship `libgif` or expose only -lgif.  Try in order
# but only when the user hasn't passed `-Dgif=disabled`; otherwise
# `dependency('libungif', required : false)` would silently flip
# HAVE_GIF on for a packager who explicitly turned the option off.
gif_opt = get_option('gif').disable_auto_if(_no_all)
if gif_opt.allowed()
  gif_dep = dependency('libungif', required : false)
  if not gif_dep.found()
    gif_dep = dependency('libgif', required : false)
  endif
  if not gif_dep.found()
    gif_dep = cc.find_library('gif', required : gif_opt)
  endif
else
  gif_dep = dependency('', required : false)
endif
if gif_dep.found()
  conf_data.set('HAVE_GIF', 1)
endif

rsvg_dep = dependency('librsvg-2.0', version : '>= 2.40.4',
                       required : get_option('rsvg').disable_auto_if(_no_all))
if rsvg_dep.found()
  conf_data.set('HAVE_RSVG', 1)
endif

# WebP definitions are split across libwebp (decode.h) and libwebpdemux
# (demux.h, which depends on libwebp).  src/image.c references symbols
# from both, so list the matched pair as a single grouped
# dependency.  Mirrors autotools' WEBP_MODULE probe at 5d78a4c
# configure.ac.
webp_opt = get_option('webp').disable_auto_if(_no_all)
webp_demux_dep = dependency('libwebpdemux', version : '>= 0.6.0',
                             required : webp_opt)
webp_lib_dep = dependency('libwebp', version : '>= 0.6.0',
                           required : webp_opt)
if webp_demux_dep.found() and webp_lib_dep.found()
  webp_dep = declare_dependency(
    dependencies : [webp_demux_dep, webp_lib_dep],
  )
  conf_data.set('HAVE_WEBP', 1)
else
  webp_dep = dependency('', required : false)
endif

# XPM is X11-only.  Bracketed by gtk3_dep.found() so a no-X build
# doesn't emit a stray HAVE_XPM that breaks src/image.c.
xpm_opt = get_option('xpm').disable_auto_if(_no_all)
if gtk3_dep.found() and xpm_opt.allowed()
  xpm_dep = dependency('xpm', required : xpm_opt)
  if xpm_dep.found()
    conf_data.set('HAVE_XPM', 1)
  endif
else
  xpm_dep = dependency('', required : false)
endif

imagemagick_opt = get_option('imagemagick')
imagemagick_dep = dependency('MagickWand', required : imagemagick_opt)
if imagemagick_dep.found()
  conf_data.set('HAVE_IMAGEMAGICK', 1)
endif

# ----------------------------------------------------------------------
# Misc system libraries (configure.ac:544-619).
# ----------------------------------------------------------------------
lcms2_dep = dependency('lcms2',
                        required : get_option('lcms2').disable_auto_if(_no_all))
if lcms2_dep.found()
  conf_data.set('HAVE_LCMS2', 1)
endif

dbus_dep = dependency('dbus-1',
                       required : get_option('dbus').disable_auto_if(_no_all))
if dbus_dep.found()
  conf_data.set('HAVE_DBUS', 1)
endif

# GPM only makes sense on GNU/Linux; skip the probe elsewhere.
gpm_opt = get_option('gpm').disable_auto_if(_no_all)
if is_linux and gpm_opt.allowed()
  gpm_dep = cc.find_library('gpm', required : gpm_opt)
elif gpm_opt.enabled()
  error('gpm=enabled but the host is not GNU/Linux')
else
  gpm_dep = dependency('', required : false)
endif
if gpm_dep.found()
  conf_data.set('HAVE_GPM', 1)
endif

# GSettings shares the gio-2.0 dependency.  Set HAVE_GSETTINGS only
# when the matching schema-compiler is also present, so the install
# step's glib-compile-schemas pass can run.  When --gsettings=enabled
# the schema-compiler must also exist; defer to find_program's
# `required` to enforce.
gsettings_opt = get_option('gsettings').disable_auto_if(_no_all)
gio_dep = dependency('gio-2.0', required : gsettings_opt)
gsettings_compile_prog = find_program('glib-compile-schemas',
                                       required : gsettings_opt)
if gio_dep.found() and gsettings_compile_prog.found()
  conf_data.set('HAVE_GSETTINGS', 1)
endif

selinux_dep = dependency('libselinux',
                          required : get_option('selinux').disable_auto_if(_no_all))
if selinux_dep.found()
  conf_data.set('HAVE_LIBSELINUX', 1)
endif

zlib_dep = dependency('zlib',
                       required : get_option('zlib').disable_auto_if(_no_all))
if zlib_dep.found()
  conf_data.set('HAVE_ZLIB', 1)
endif

libotf_dep = dependency('libotf',
                         required : get_option('libotf').disable_auto_if(_no_all))
if libotf_dep.found()
  conf_data.set('HAVE_LIBOTF', 1)
endif

m17n_flt_dep = dependency('m17n-flt',
                           required : get_option('m17n-flt').disable_auto_if(_no_all))
if m17n_flt_dep.found()
  conf_data.set('HAVE_M17N_FLT', 1)
endif

# ----------------------------------------------------------------------
# Sound (configure.ac:424-463).  Linux uses ALSA; *BSD uses
# bsd-ossaudio; OSS is pretty much dead but kept as a manual
# selector.  meson.options' `sound` combo accepts auto/yes/no/alsa/
# oss/bsd-ossaudio.
# ----------------------------------------------------------------------
sound_choice = get_option('sound')
alsa_dep = dependency('', required : false)
if sound_choice == 'auto' or sound_choice == 'yes' or sound_choice == 'alsa'
  alsa_dep = dependency('alsa', required : sound_choice == 'alsa')
endif
if alsa_dep.found()
  conf_data.set('HAVE_SOUND', 1)
  conf_data.set('HAVE_ALSA', 1)
  conf_data.set('USE_ALSA', 1)
elif sound_choice == 'bsd-ossaudio'
  conf_data.set('HAVE_SOUND', 1)
  # bsd-ossaudio's interface is via -lossaudio; defer linking detail
  # to the source-tree consumer (sound.c).
endif

# ----------------------------------------------------------------------
# Dynamic modules (configure.ac:--with-modules).  HAVE_MODULES gates
# the compilation of src/dynlib.c's full path; the suffix for the
# DEFINE_MODULE / EMACS_MAJOR_VERSION wiring is already in conf_data
# above (MODULES_SUFFIX).
# ----------------------------------------------------------------------
modules_opt = get_option('modules').disable_auto_if(_no_all)
if modules_opt.allowed()
  if cc.has_function('dlopen') or cc.has_function('dlopen',
                                                   args : '-ldl')
    conf_data.set('HAVE_MODULES', 1)
  elif modules_opt.enabled()
    error('--with-modules=enabled but neither dlopen nor -ldl found')
  endif
endif

# ----------------------------------------------------------------------
# Elisp threading (configure.ac:--with-threads).  pthread is already
# linked unconditionally; HAVE_THREADS is the source-tree gate.
# ----------------------------------------------------------------------
threads_opt = get_option('threads').disable_auto_if(_no_all)
if threads_opt.allowed()
  conf_data.set('HAVE_THREADS', 1)
endif

# ----------------------------------------------------------------------
# Cairo XCB (configure.ac:--with-cairo-xcb), XInput 2 extension,
# Xaw3d.  All X11-gated; explicit `enabled` errors out without GTK3.
# ----------------------------------------------------------------------
xinput2_opt = get_option('xinput2').disable_auto_if(_no_all)
xdbe_opt = get_option('xdbe').disable_auto_if(_no_all)
if gtk3_dep.found()
  if xinput2_opt.allowed()
    if cc.has_header('X11/extensions/XInput2.h')
      conf_data.set('HAVE_XINPUT2', 1)
    elif xinput2_opt.enabled()
      error('xinput2=enabled but X11/extensions/XInput2.h not found')
    endif
  endif
  if xdbe_opt.allowed()
    if cc.has_header('X11/extensions/Xdbe.h')
      conf_data.set('HAVE_XDBE', 1)
    elif xdbe_opt.enabled()
      error('xdbe=enabled but X11/extensions/Xdbe.h not found')
    endif
  endif
elif xinput2_opt.enabled() or xdbe_opt.enabled()
  error('xinput2/xdbe=enabled but GTK3/X11 not in use')
endif

# ----------------------------------------------------------------------
# X11 input method (configure.ac:4395-4410 at anchor 08a22b8965ec).
# autotools defines HAVE_XIM whenever X11 is in use AND --without-xim
# was not passed; USE_XIM is the runtime default for the
# `x-use-xim' Lisp variable.
# ----------------------------------------------------------------------
xim_opt = get_option('xim').disable_auto_if(_no_all)
if gtk3_dep.found() and xim_opt.allowed()
  conf_data.set('HAVE_XIM', 1)
  conf_data.set('USE_XIM', 1)
elif xim_opt.enabled() and not gtk3_dep.found()
  error('xim=enabled but X11 is not in use')
endif

# ----------------------------------------------------------------------
# Developer / debugging knobs (configure.ac --enable-gc-mark-trace,
# --enable-profiling, --enable-build-details at anchor 08a22b8965ec).
# ----------------------------------------------------------------------
# When gc-mark-trace is on, AC_DEFINE GC_REMEMBER_LAST_MARKED enables
# the mark-trace ring buffer in src/alloc.c (used by the GC debug
# commands).  Default off matches the boolean option's value in
# meson.options:193 -- developers opt in via -Dgc-mark-trace=true.
if get_option('gc-mark-trace')
  conf_data.set('GC_REMEMBER_LAST_MARKED', 1)
endif

# build-details is consumed at dump time as `--no-build-details', not
# at compile time; the flag is plumbed through meson/run_dump.py via
# the bootstrap_pdmp / emacs_pdmp custom_targets.  Stash the boolean
# here so src/meson.build and lisp/meson.build can read it.
build_details_opt = get_option('build-details')

# ----------------------------------------------------------------------
# movemail / pop.c options (configure.ac:358-419 at anchor
# 08a22b8965ec).  Probe libraries here so lib-src can pick up the
# extra link args; defines land in conf_data.
# ----------------------------------------------------------------------
movemail_extra_libs = []

# --with-mailutils -- when true, GNU Mailutils is preferred and
# movemail is NOT installed (the install gate lives in
# lib-src/meson.build).  HAVE_MAILUTILS is consumed by src/callproc.c.
mailutils_opt = get_option('mailutils')
if mailutils_opt.allowed() and dependency('mailutils', required : false).found()
  conf_data.set('HAVE_MAILUTILS', 1)
elif mailutils_opt.enabled()
  error('mailutils=enabled but no mailutils pkg-config file found')
endif
mailutils_install_movemail = not conf_data.has('HAVE_MAILUTILS')

# --with-pop -- enables POP3 in movemail (MAIL_USE_POP).
pop_opt = get_option('pop')
if pop_opt.allowed()
  conf_data.set('MAIL_USE_POP', 1)
endif

# --with-kerberos / --with-kerberos5 -- POP authentication backends.
kerberos_opt = get_option('kerberos')
if kerberos_opt.allowed()
  _krb = cc.find_library('krb', required : kerberos_opt)
  if not _krb.found()
    _krb = cc.find_library('krb4', required : false)
  endif
  if _krb.found()
    conf_data.set('KERBEROS', 1)
    movemail_extra_libs += _krb
    foreach _lib : ['des', 'des425']
      _dep = cc.find_library(_lib, required : false)
      if _dep.found()
        movemail_extra_libs += _dep
        break
      endif
    endforeach
  endif
endif

kerberos5_opt = get_option('kerberos5')
if kerberos5_opt.allowed()
  _krb5 = cc.find_library('krb5', required : kerberos5_opt)
  if _krb5.found()
    conf_data.set('KERBEROS', 1)
    conf_data.set('KERBEROS5', 1)
    movemail_extra_libs += _krb5
    foreach _lib : ['k5crypto', 'crypto']
      _dep = cc.find_library(_lib, required : false)
      if _dep.found()
        movemail_extra_libs += _dep
        break
      endif
    endforeach
    _comerr = cc.find_library('com_err', required : false)
    if _comerr.found()
      movemail_extra_libs += _comerr
    endif
  endif
endif

# --with-hesiod -- POP-host lookup (HESIOD + -lhesiod -lresolv).
hesiod_opt = get_option('hesiod')
if hesiod_opt.allowed()
  _hesiod = cc.find_library('hesiod', required : hesiod_opt)
  if _hesiod.found()
    conf_data.set('HESIOD', 1)
    movemail_extra_libs += _hesiod
    _resolv = cc.find_library('resolv', required : false)
    if _resolv.found()
      movemail_extra_libs += _resolv
    endif
  endif
endif

# --with-mail-unlink -- empty vs. unlink the mail spool after read.
if get_option('mail-unlink')
  conf_data.set('MAIL_UNLINK_SPOOL', 1)
endif

# --with-mailhost=HOSTNAME -- default POP host.
_mailhost = get_option('mailhost')
if _mailhost != ''
  conf_data.set_quoted('MAILHOST', _mailhost)
endif

# ----------------------------------------------------------------------
# Toolkit scroll bars (configure.ac:566, 4360-4385 at anchor
# 08a22b8965ec).  configure.ac defines USE_TOOLKIT_SCROLL_BARS when
# any window-system toolkit is in use and --with-toolkit-scroll-bars
# is not explicitly off.  The legacy LUCID/Motif/Xaw3d branches are
# dropped here because those toolkits are no longer supported
# (meson.options:52-53).
# ----------------------------------------------------------------------
toolkit_scroll_bars_opt = get_option('toolkit-scroll-bars').disable_auto_if(_no_all)
_have_toolkit_for_scrollbars = (gtk3_dep.found()
                                or conf_data.has('HAVE_NS'))
if toolkit_scroll_bars_opt.allowed() and _have_toolkit_for_scrollbars
  conf_data.set('USE_TOOLKIT_SCROLL_BARS', 1)
elif toolkit_scroll_bars_opt.enabled() and not _have_toolkit_for_scrollbars
  error('toolkit-scroll-bars=enabled but no window-system toolkit is in use')
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

# C99 flexible array member support (gnulib's flexmember.m4 upstream).
# If the compiler accepts `char name[];` as a flexible array, define
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
subdir('leim')     # quail input-method tables + leim-list.el
subdir('lisp')     # byte-compile + native-comp + emacs.pdmp
subdir('test')     # ERT test discovery
subdir('doc')      # texinfo info manuals
if is_darwin and get_option('ns').allowed()
  subdir('nextstep')  # macOS Cocoa Emacs.app bundle
endif
# Parked subdirs -- see .claude/notes/build-system.md "Parked / unsupported".
# Their autotools recipes live at anchor commit 08a22b8965ec; reviving
# any of them is a substantial cross-compile or platform-port effort
# rather than an incremental Meson translation.
# subdir('java')           # parked: Android cross-build
# subdir('exec')           # parked: Android cross-build helper
# subdir('cross')          # parked: Android cross-build host
# subdir('cross/ndk-build') # parked: Android NDK glue
# subdir('admin/grammars') # parked: bovine/wisent regen; outputs committed

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

# GSettings schema (Makefile.in:947-985).  Installed when both
# gio-2.0 and glib-compile-schemas are present.  meson_install.py
# runs `glib-compile-schemas` post-install so the dconf cache picks
# up the new schema.
if conf_data.has('HAVE_GSETTINGS')
  install_data(
    'etc/org.gnu.emacs.defaults.gschema.xml',
    install_dir : gsettingsschemadir,
  )
endif

# Per-build artefacts (etc/DOC, native-lisp/, subdirs.el creation,
# emacs/emacs.pdmp from build tree, gameuser sgid bit).  These need
# the build outputs to exist on disk, so they run from the post-build
# install script.
_install_args = [
  '--prefix',                 prefix,
  '--bindir',                 bindir,
  '--datadir',                emacs_data,
  '--libexecdir',             emacs_arch,
  '--mandir',                 mandir,
  '--infodir',                infodir,
  '--gsettingsschemadir',     gsettingsschemadir,
  '--build-root',             meson.global_build_root(),
  '--source-root',            meson.global_source_root(),
  '--version',                emacs_version,
  '--gameuser',               get_option('gameuser'),
  '--update-subdirs',
  meson.global_source_root() / 'build-aux' / 'update-subdirs',
]
if get_option('compress-install')
  _install_args += '--compress-install'
endif
meson.add_install_script(
  py, files('meson/meson_install.py'), _install_args,
)
