# test/meson.build -- ERT test discovery for `meson test`.
#
# STATUS: phase 7 starter.  Discovers test/**/*-tests.el at meson
# configure time and registers each as a `test()` so `meson test
# -C build` runs them.  Per-file invocation matches the autotools
# pattern in test/Makefile.in:81 (--eval (ert (quote SELECTOR))).
#
# The full ERT suite under autotools is `make check` from the top
# level; the meson equivalent is `meson test -C build`.  See
# .claude/plans/migrate-from-current-build-replicated-gadget.md.

# ----------------------------------------------------------------------
# Discovery: walk test/ for *-tests.el files.  Mirrors
# test/Makefile.in's $(setwins).
# ----------------------------------------------------------------------
list_tests = files('../meson/list_test_files.py')
test_manifest = custom_target(
  'test-manifest',
  output : 'test.manifest',
  command : [
    py, list_tests,
    '--test-dir', meson.global_source_root() / 'test',
    '--output',   '@OUTPUT@',
  ],
)

# Test runner.  Mirrors test/Makefile.in:81-153 for the default
# selector (excludes :expensive-test and :unstable).  The runner
# script handles the bootstrap-emacs invocation, env vars and the
# ert exit code interpretation.
run_test = files('../meson/run_test.py')

# Smoke-test set: a small handful of self-contained test files we
# know pass cleanly.  The full discovery loop runs only when the
# manifest custom_target output is consumed by something; meson
# can't enumerate at configure time without breaking re-discovery
# on .el changes.  So we register a static smoke set plus a
# meta-test that exercises the manifest.
smoke_tests = [
  'lisp/subr-tests.el',
  'lisp/sort-tests.el',
  'lisp/dom-tests.el',
]

foreach rel : smoke_tests
  name = rel.replace('/', '_').replace('.el', '')
  test(
    name,
    py,
    args : [
      run_test,
      '--bootstrap-emacs', bootstrap_emacs.full_path(),
      '--source-root',     meson.global_source_root(),
      '--test-file',       meson.global_source_root() / 'test' / rel,
    ],
    depends : [bootstrap_emacs, charscript_el, emoji_zwj_el, charsets_stamp],
    timeout : 120,
    suite : ['lisp', 'smoke'],
  )
endforeach
