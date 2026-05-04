# test/src/emacs-module-resources/meson.build -- mod-test shared module.
#
# emacs-module-tests.el loads the module from
# `<invocation-directory>/../test/src/emacs-module-resources/mod-test`
# at runtime; running emacs lives in build/src, so the target must
# emit at build/test/src/emacs-module-resources/mod-test.so.
# Declaring the shared_module from this directory's meson.build
# places it there naturally (the build dir mirrors the source tree).

mod_test = shared_module(
  'mod-test',
  sources : [files('mod-test.c'), emacs_module_h],
  include_directories : [
    top_inc,                          # picks up generated config.h
    include_directories('.', '../../../src', '../../../lib'),
  ],
  dependencies : [gmp_dep, libgnu_dep],
  c_args : ['-fPIC'],
  install : false,
  name_prefix : '',                   # mod-test.so, not libmod-test.so
)
