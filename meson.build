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

# ----------------------------------------------------------------------
# Compiler probes used to populate src/config.h.
# ----------------------------------------------------------------------

conf_data = configuration_data()

conf_data.set_quoted('PACKAGE_NAME', 'GNU Emacs')
conf_data.set_quoted('PACKAGE_VERSION', meson.project_version())
conf_data.set_quoted('PACKAGE_STRING',
                     'GNU Emacs ' + meson.project_version())
conf_data.set_quoted('PACKAGE_BUGREPORT', 'bug-gnu-emacs@gnu.org')
conf_data.set_quoted('PACKAGE_URL', 'https://www.gnu.org/software/emacs/')
conf_data.set_quoted('PACKAGE_TARNAME', 'emacs')
conf_data.set_quoted('VERSION', meson.project_version())

# TODO(phase-2): port the m4/*.m4 feature checks here.  This stub
# config.h is enough only for the simplest lib-src host tools on Linux
# glibc; src/ and lib/ will not compile against it.
foreach hdr : [
  'fcntl.h', 'getopt.h', 'inttypes.h', 'limits.h', 'pwd.h', 'signal.h',
  'stdint.h', 'sys/stat.h', 'sys/types.h', 'unistd.h',
]
  if cc.has_header(hdr)
    conf_data.set('HAVE_' + hdr.to_upper().underscorify(), 1)
  endif
endforeach

# Generated stub.  Real content lands in Phase 2 (gnulib port).
configure_file(
  output : 'config.h',
  configuration : conf_data,
)

# include_directories('.') from the project root resolves to both the
# source tree and the build tree, so subdir Meson files can pick up
# the generated config.h via this dependency.
top_inc = include_directories('.')

emacs_version = meson.project_version()

# ----------------------------------------------------------------------
# Subdir wiring.  Each phase fills in another directory.
# ----------------------------------------------------------------------

subdir('lib')      # Phase 2: full gnulib port (currently a stub)
subdir('lib-src')  # Phase 1: helper executables (in progress)
# subdir('src')      # Phase 3: temacs, emacs binary, dumping
# subdir('lisp')     # Phase 4-5: byte-compile + native-comp
# subdir('leim')     # Phase 6
# subdir('admin')    # Phase 6: charsets, grammars, unidata
# subdir('doc')      # Phase 6: texinfo manuals
# subdir('test')     # Phase 7: ERT
# subdir('nextstep') # Phase 8: macOS .app
# subdir('java')     # Phase 8: Android cross-build
