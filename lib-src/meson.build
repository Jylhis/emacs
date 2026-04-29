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
