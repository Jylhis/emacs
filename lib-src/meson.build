# lib-src/meson.build -- helper executables that ship with Emacs.
#
# STATUS: Phase 1-2 in progress.  Currently builds only the bootstrap
# helpers (make-docfile, make-fingerprint), which are the simplest
# tools and the ones src/ needs to bootstrap the main emacs binary.
# Other tools (etags, ebrowse, emacsclient, hexl, movemail,
# update-game-score) are deferred until phase 2 grows enough gnulib
# coverage to support them; see the TODO at the bottom of this file.

lib_src_inc = [
  top_inc,                       # picks up the generated config.h
  include_directories('.', '../src', '../lib'),
]

lib_src_args = []

# Build-time helpers (Makefile.in:158, never installed).  These run
# during the Emacs bootstrap to produce etc/DOC and the dump
# fingerprint.
make_docfile = executable('make-docfile',
  sources : files('make-docfile.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

make_fingerprint = executable('make-fingerprint',
  sources : files('make-fingerprint.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

# Probe whether each remaining tool compiles with the current libgnu
# coverage; flip to executable() once the helper compiles.
# (Re-enabled incrementally as phase 2 fills in more gnulib pieces.)
hexl = executable('hexl',
  sources : files('hexl.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

update_game_score = executable('update-game-score',
  sources : files('update-game-score.c'),
  include_directories : lib_src_inc,
  # configure.ac:656 sets gamedir; use an empty string until phase 9
  # wires up the install rules and gamedir option.
  c_args : lib_src_args + ['-DHAVE_SHARED_GAME_DIR=""'],
  dependencies : libgnu_dep,
  install : false,
)

ebrowse = executable('ebrowse',
  sources : files('ebrowse.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

# emacsclient depends on file_has_acl which needs libacl detection
# (m4/acl.m4) and conditional inclusion of lib/file-has-acl.c plus
# its dependencies.  Deferred to the next phase 2 commit.
# emacsclient = executable('emacsclient',
#   sources : files('emacsclient.c'),
#   include_directories : lib_src_inc,
#   c_args : lib_src_args,
#   dependencies : libgnu_dep,
#   install : true,
# )

movemail = executable('movemail',
  sources : files('movemail.c', 'pop.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : false,
)

etags = executable('etags',
  sources : files('etags.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

# TODO(phase-2): the following tools also need to be wired but require
# gnulib pieces that have not been ported yet:
#
#   etags        -- needs <stdckdint.h> (lib/stdckdint.in.h substitution).
#   ebrowse      -- compiles, but pulls more gnulib headers we haven't
#                   covered yet.
#   emacsclient  -- needs ATTRIBUTE_FORMAT_PRINTF visibility from
#                   conf_post.h plus various pkg-config-detected libs
#                   (acl, libcom_err, libresolv).
#   hexl         -- needs binary-io.h with a real fcntl substitute.
#   movemail     -- needs liblockfile/libmail detection plus pop.c.
#   update-game-score -- needs HAVE_SHARED_GAME_DIR plumbing through
#                   meson.options.
#   seccomp-filter -- needs pkg-config('libseccomp'); x86_64-only.
#   asset-directory-tool -- Android-only; lives in java/meson.build.
#
# See .claude/plans/migrate-from-current-build-replicated-gadget.md
# for the migration plan.
