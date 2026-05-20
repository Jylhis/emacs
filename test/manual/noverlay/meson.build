# test/manual/noverlay/meson.build -- itree.c interval-tree tests.
#
# Builds a standalone C test binary that links against src/itree.c
# directly (via emacs-compat.h to stand in for the rest of the Emacs
# environment) and uses libcheck as the unit-test framework.  Mirrors
# the deleted test/manual/noverlay/Makefile.in at anchor 08a22b8965ec.
#
# Manual test: build_by_default false; not registered as a meson test
# because it requires libcheck and is intended for itree development
# triage.  Run with:
#
#     meson compile -C build itree-tests
#     ./build/test/manual/noverlay/itree-tests

check_dep = dependency('check', required : false)

if check_dep.found()
  itree_tests = executable(
    'itree-tests',
    sources : files('itree-tests.c'),
    include_directories : [
      top_inc,
      include_directories('.', '../../../src'),
    ],
    dependencies : [check_dep, libgnu_dep],
    install : false,
    build_by_default : false,
  )
endif
