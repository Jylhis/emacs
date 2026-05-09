# nextstep/meson.build -- assemble Emacs.app bundle for macOS Cocoa.
#
# Mirrors nextstep/Makefile.in at anchor 08a22b8965ec.  Runs only on
# darwin AND when -Dns is allowed (auto on darwin by default).
# Produces build/nextstep/Emacs.app, a fully launchable macOS .app
# whose CFBundleExecutable resolves to Contents/MacOS/Emacs.
#
# When -Dns-self-contained is allowed (default auto on darwin), the
# bundle additionally embeds lisp/, etc/, info/, and emacs.pdmp under
# Contents/Resources/ so it can run without the global install tree.

ns_appname = 'Emacs.app'
ns_bundle_dir = meson.current_build_dir() / ns_appname

# ----------------------------------------------------------------------
# configure_file substitutions for Info.plist / Emacs.desktop /
# InfoPlist.strings.  Mirrors autotools' AC_SUBST list at
# configure.ac NS section.
# ----------------------------------------------------------------------
ns_plist_data = configuration_data()
ns_plist_data.set('version', meson.project_version())
ns_plist_data.set('PACKAGE_BUGREPORT', 'bug-gnu-emacs@gnu.org')
ns_plist_data.set('copyright',
                   'Copyright (C) 2026 Free Software Foundation, Inc.')
# arch-independent build year used by some plist substitutions.
ns_plist_data.set('year', '2026')

info_plist = configure_file(
  input         : files('templates/Info.plist.in'),
  output        : 'Info.plist',
  configuration : ns_plist_data,
)
configure_file(
  input         : files('templates/Info-gnustep.plist.in'),
  output        : 'Info-gnustep.plist',
  configuration : ns_plist_data,
)
configure_file(
  input         : files('templates/Emacs.desktop.in'),
  output        : 'Emacs.desktop',
  configuration : ns_plist_data,
)
configure_file(
  input         : files('templates/InfoPlist.strings.in'),
  output        : 'InfoPlist.strings',
  configuration : ns_plist_data,
)

# ----------------------------------------------------------------------
# Bundle assembly.  The custom_target uses a stamp because Emacs.app
# is a directory; we report the stamp as the meson-tracked output and
# leave the bundle layout for run_app_bundle.py to manage.
# ----------------------------------------------------------------------
run_app_bundle = files('../meson/run_app_bundle.py')

ns_bundle_args = [
  py, run_app_bundle,
  '--skeleton',     meson.global_source_root() / 'nextstep/Cocoa/Emacs.base',
  '--bundle',       ns_bundle_dir,
  '--info-plist',   info_plist,
  '--emacs-binary', emacs.full_path(),
  '--stamp',        '@OUTPUT@',
]
ns_bundle_deps = [emacs]

# Self-contained Emacs.app -- copying lisp/, etc/, info/, emacs.pdmp
# into Contents/Resources/ -- is wired by ns-self-contained in a
# follow-up commit (D5 in the migration plan).  Today the bundle
# launches the system-wide installed Emacs tree at runtime.

ns_bundle_stamp = custom_target(
  'emacs-app-bundle',
  output  : 'emacs-app.stamp',
  command : ns_bundle_args,
  depends : ns_bundle_deps,
  build_by_default : true,
)
