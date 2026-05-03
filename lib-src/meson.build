# lib-src/meson.build -- helper executables that ship with Emacs.
#
# bindir tools (run directly by users):   etags, ctags, ebrowse,
#                                         emacsclient.
# emacs_arch tools (run by emacs):        hexl, movemail, update-game-score.
# never installed (build-only helpers):   make-docfile, make-fingerprint.
#
# Reference: lib-src/Makefile.in INSTALLABLES (bindir) + UTILITIES
# (libexec/emacs/VERSION/CONFIG/) at 5d78a4c.

lib_src_inc = [
  top_inc,                       # picks up the generated config.h
  include_directories('.', '../src', '../lib'),
]

lib_src_args = []

# update-game-score sgid handling.  When `gameuser` is non-empty,
# autotools embeds the shared game directory at compile time and
# installs the binary sgid to that user/group (Makefile.in:656-680).
# Without a shared gamedir, score files are written to user $HOME and
# no privileges are needed.
gameuser = get_option('gameuser')
gamedir = ''
if gameuser != ''
  gamedir = get_option('localstatedir') / 'games' / 'emacs'
endif
ugs_cflags = lib_src_args + [
  '-DHAVE_SHARED_GAME_DIR="' + gamedir + '"',
]

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

hexl = executable('hexl',
  sources : files('hexl.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
  install_dir : emacs_arch,
)

update_game_score = executable('update-game-score',
  sources : files('update-game-score.c'),
  include_directories : lib_src_inc,
  c_args : ugs_cflags,
  dependencies : libgnu_dep,
  install : true,
  install_dir : emacs_arch,
  # When a shared gamedir is configured, the autotools build installs
  # this sgid to ${gameuser}.  meson can't set sgid bits portably from
  # install_data, so meson_install.py applies the mode + ownership
  # post-install.
)

ebrowse = executable('ebrowse',
  sources : files('ebrowse.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

emacsclient = executable('emacsclient',
  sources : files('emacsclient.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

movemail = executable('movemail',
  sources : files('movemail.c', 'pop.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
  install_dir : emacs_arch,
)

etags = executable('etags',
  sources : files('etags.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : libgnu_dep,
  install : true,
)

# ctags is etags built with -DCTAGS=1 (Makefile.in:282-285).  Build a
# second executable rather than a runtime symlink so `--help` and the
# binary's own argv[0] sniffing work.
ctags = executable('ctags',
  sources : files('etags.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args + ['-DCTAGS=1'],
  dependencies : libgnu_dep,
  install : true,
)

# rcs2log is a shell script (Makefile.in SCRIPTS=rcs2log).
install_data(
  'rcs2log',
  install_dir : emacs_arch,
  install_mode : 'rwxr-xr-x',
)
