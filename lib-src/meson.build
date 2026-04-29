# lib-src/meson.build -- helper executables that ship with Emacs.
#
# STATUS: Phase 1 of the migration plan.  Wires every executable
# defined in lib-src/Makefile.in (lines 260-435) but cannot link
# successfully until lib/meson.build (Phase 2) provides a real
# libgnu.a.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md for
# the phase plan and dependency chain.

lib_src_inc = [
  top_inc,                       # picks up the generated config.h
  include_directories('.', '../src', '../lib'),
]

# Common compile arguments mirroring BASE_CFLAGS in
# lib-src/Makefile.in:246.
lib_src_args = []

# Executables installed for end users (Makefile.in:149).
executable('etags',
  sources : files('etags.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

executable('ebrowse',
  sources : files('ebrowse.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

executable('emacsclient',
  sources : files('emacsclient.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

# Internal utilities (Makefile.in:153).  Installed under archlibdir,
# not bindir; we'll wire that distinction in Phase 9 (install).
executable('hexl',
  sources : files('hexl.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

executable('movemail',
  sources : files('movemail.c', 'pop.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

executable('update-game-score',
  sources : files('update-game-score.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args + [
    '-DHAVE_SHARED_GAME_DIR=""',
  ],
  dependencies : libgnu_dep,
  install : false,
)

# Build-time helpers (Makefile.in:158, never installed).  These run
# during the Emacs bootstrap; they have to be host binaries even on
# Android cross-builds.
executable('make-docfile',
  sources : files('make-docfile.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

executable('make-fingerprint',
  sources : files('make-fingerprint.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

# TODO(phase-1): seccomp-filter (lib-src/Makefile.in:427) needs
# pkg-config('libseccomp') and is x86_64-only -- gate behind a feature
# detection.

# TODO(phase-1): asset-directory-tool (lib-src/Makefile.in:392) is
# Android-only; wire under java/meson.build in Phase 8.
