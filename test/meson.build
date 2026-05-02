# test/meson.build -- ERT test discovery for `meson test`.
#
# Discovers test/**/*-tests.el at configure time via run_command()
# and registers each as a test().  Per-file invocation mirrors the
# autotools pattern (--eval (ert (quote SELECTOR))).
#
# Usage:
#   meson test -C build                   # all tests
#   meson test -C build --suite smoke     # fast confidence check
#   meson test -C build --suite lisp      # lisp-level tests only
#   meson test -C build --suite src       # C-level tests only

# ----------------------------------------------------------------------
# Discovery: enumerate test/**/*-tests.el at configure time.
# Follows the pattern in lisp/meson.build:107-112.
# ----------------------------------------------------------------------
list_tests = files('../meson/list_test_files.py')
_all_test_files = run_command(
  py, list_tests,
  '--test-dir', meson.global_source_root() / 'test',
  '--output',   '/dev/stdout',
  check : true,
).stdout().strip().split('\n')

# Manifest custom_target -- useful for debugging (ninja test-manifest).
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
# selector (excludes :expensive-test and :unstable).
run_test = files('../meson/run_test.py')

# Smoke-test set: a small handful of self-contained test files we
# know pass cleanly.  These get an extra 'smoke' suite tag.
smoke_set = [
  'lisp/subr-tests.el',
  'lisp/sort-tests.el',
  'lisp/dom-tests.el',
]

foreach rel : _all_test_files
  if rel == ''
    continue
  endif

  # manual/ tests require a display / GUI session; skip.
  if rel.startswith('manual/')
    continue
  endif

  # Assign suite based on top-level directory.
  if rel.startswith('src/')
    _suite = ['src']
  elif rel.startswith('lib-src/')
    _suite = ['lib-src']
  else
    _suite = ['lisp']
  endif

  if smoke_set.contains(rel)
    _suite += 'smoke'
  endif

  name = rel.replace('/', '_').replace('.el', '')
  test(
    name,
    py,
    args : [
      run_test,
      '--emacs',       emacs.full_path(),
      '--dump-file',   emacs_pdmp.full_path(),
      '--source-root', meson.global_source_root(),
      '--test-file',   meson.global_source_root() / 'test' / rel,
    ],
    depends : [emacs, emacs_pdmp],
    timeout : 120,
    suite : _suite,
  )
endforeach
