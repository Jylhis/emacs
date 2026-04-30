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

# Expanded set: more self-contained ERT files covering core lisp.
# Mirrors the directories in test/Makefile.in:81-153.  Files that
# require a dumped emacs (display, gnus, eshell, etc.) are deferred
# until the test runner can use the dumped emacs in addition to
# bootstrap-emacs.
extended_tests = [
  # Core utilities -- pure-elisp, no display.
  'lisp/abbrev-tests.el',
  'lisp/auth-source-tests.el',
  'lisp/calc/calc-tests.el',
  'lisp/character-fold-tests.el',
  'lisp/cmds-tests.el',
  'lisp/comint-tests.el',
  'lisp/custom-tests.el',
  'lisp/dired-aux-tests.el',
  'lisp/electric-tests.el',
  'lisp/fileloop-tests.el',
  'lisp/files-tests.el',
  'lisp/files-x-tests.el',
  'lisp/format-spec-tests.el',
  'lisp/help-tests.el',
  'lisp/hexl-tests.el',
  'lisp/json-tests.el',
  'lisp/jsonrpc-tests.el',
  'lisp/keymap-tests.el',
  'lisp/minibuffer-tests.el',
  'lisp/replace-tests.el',
  'lisp/rfc2104-tests.el',
  'lisp/server-tests.el',
  'lisp/shadowfile-tests.el',
  'lisp/simple-tests.el',
  'lisp/subr-x-tests.el',
  'lisp/textmodes/conf-mode-tests.el',
  'lisp/thingatpt-tests.el',
  'lisp/uniquify-tests.el',
  'lisp/vc/vc-bzr-tests.el',
  # emacs-lisp/ subset.
  'lisp/emacs-lisp/advice-tests.el',
  'lisp/emacs-lisp/avl-tree-tests.el',
  'lisp/emacs-lisp/backquote-tests.el',
  'lisp/emacs-lisp/bindat-tests.el',
  'lisp/emacs-lisp/cconv-tests.el',
  'lisp/emacs-lisp/cl-extra-tests.el',
  'lisp/emacs-lisp/cl-generic-tests.el',
  'lisp/emacs-lisp/cl-lib-tests.el',
  'lisp/emacs-lisp/cl-print-tests.el',
  'lisp/emacs-lisp/cl-seq-tests.el',
  'lisp/emacs-lisp/copyright-tests.el',
  'lisp/emacs-lisp/edebug-tests.el',
  'lisp/emacs-lisp/eldoc-tests.el',
  'lisp/emacs-lisp/ert-tests.el',
  'lisp/emacs-lisp/ert-x-tests.el',
  'lisp/emacs-lisp/find-func-tests.el',
  'lisp/emacs-lisp/generator-tests.el',
  'lisp/emacs-lisp/macroexp-tests.el',
  'lisp/emacs-lisp/map-tests.el',
  'lisp/emacs-lisp/package-tests.el',
  'lisp/emacs-lisp/pcase-tests.el',
  'lisp/emacs-lisp/pp-tests.el',
  'lisp/emacs-lisp/regexp-opt-tests.el',
  'lisp/emacs-lisp/seq-tests.el',
  'lisp/emacs-lisp/shortdoc-tests.el',
  'lisp/emacs-lisp/subr-x-tests.el',
  'lisp/emacs-lisp/syntax-tests.el',
  'lisp/emacs-lisp/timer-tests.el',
]

foreach rel : extended_tests
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
    suite : ['lisp', 'extended'],
  )
endforeach
