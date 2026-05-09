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

# update-game-score: shared gamedir handling.  Autotools logic
# (configure.ac:656-680, lib-src/Makefile.in:163-167):
#
#   --with-gameuser=alice     -> user mode  (chown alice + chmod u+s)
#   --with-gameuser=:games    -> group mode (chgrp games + chmod g+s)
#   (unset / empty)           -> no shared gamedir; the binary is NOT
#                                installed (UTILITIES gates on
#                                $(use_gamedir)).
#
# When the option is empty, autotools builds update-game-score as a
# build-tree helper but skips installation; without a shared gamedir
# Emacs writes per-user score files itself.
gameuser = get_option('gameuser')
ugs_install = gameuser != ''
gamedir = ''
if ugs_install
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
  install : ugs_install,
  install_dir : emacs_arch,
  # The setuid / setgid bit + chown / chgrp are applied post-install
  # by meson/meson_install.py based on the gameuser option's form
  # (bare USER vs. ":GROUP"); install_dir is ignored when
  # install: false.
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

# movemail is NOT installed when --with-mailutils=true (configure.ac
# UTILITIES filter at anchor 08a22b8965ec lib-src/Makefile.in:163).
# It still builds either way so test/lib-src/* exercises stay green.
movemail = executable('movemail',
  sources : files('movemail.c', 'pop.c'),
  include_directories : lib_src_inc,
  c_args : lib_src_args,
  dependencies : [libgnu_dep] + movemail_extra_libs,
  install : mailutils_install_movemail,
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

# ----------------------------------------------------------------------
# seccomp-filter -- Linux Secure Computing filter generator.
# Mirrors the gates in lib-src/Makefile.in:225-249 at anchor
# 08a22b8965ec: Linux + x86_64 + libseccomp present.  The binary is
# build-only (DONT_INSTALL); the .bpf and .pfc filter files it
# emits are installed under emacs_arch so the daemon mode can load
# them at runtime.
# ----------------------------------------------------------------------
if is_linux and host_machine.cpu_family() == 'x86_64'
  libseccomp_dep = dependency('libseccomp', required : false)
  if libseccomp_dep.found()
    seccomp_filter = executable('seccomp-filter',
      sources : files('seccomp-filter.c'),
      include_directories : lib_src_inc,
      c_args : lib_src_args,
      dependencies : [libgnu_dep, libseccomp_dep],
      install : false,
    )
    custom_target('seccomp-bpf',
      output : [
        'seccomp-filter.bpf', 'seccomp-filter.pfc',
        'seccomp-filter-exec.bpf', 'seccomp-filter-exec.pfc',
      ],
      command : [
        seccomp_filter,
        '@OUTPUT0@', '@OUTPUT1@',
        '@OUTPUT2@', '@OUTPUT3@',
      ],
      install : true,
      install_dir : emacs_arch,
      build_by_default : true,
    )
  endif
endif
