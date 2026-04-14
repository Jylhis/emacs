# Emacs Testing

Write and run ERT tests for GNU Emacs changes.

## When to Use

Use when writing new tests, fixing test failures, or validating changes.

## Test File Convention

Tests for `lisp/foo/bar.el` go in `test/lisp/foo/bar-tests.el`.
Tests for `src/eval.c` go in `test/src/eval-tests.el`.

### Test File Template

```elisp
;;; bar-tests.el --- Tests for bar.el  -*- lexical-binding: t; -*-

;; Copyright (C) 2026 Free Software Foundation, Inc.

;;; Commentary:

;; Tests for lisp/foo/bar.el

;;; Code:

(require 'ert)
(require 'bar)

(ert-deftest bar-tests-basic-functionality ()
  "Verify bar-do-thing handles normal input."
  (should (equal (bar-do-thing "input") "expected")))

(ert-deftest bar-tests-edge-case-nil ()
  "Verify bar-do-thing handles nil gracefully."
  (should-error (bar-do-thing nil) :type 'wrong-type-argument))

(ert-deftest bar-tests-expensive-operation ()
  "Verify bar-process-all with large dataset."
  :tags '(:expensive-test)
  (should (bar-process-all (make-list 10000 'item))))

;;; bar-tests.el ends here
```

## ERT Assertions

```elisp
(should FORM)                              ; FORM must be non-nil
(should-not FORM)                          ; FORM must be nil
(should-error FORM :type 'error-symbol)    ; FORM must signal error
(should (equal ACTUAL EXPECTED))           ; Equality test
(should (string-match REGEXP STRING))      ; Regexp match
```

## Test Tags

- `:expensive-test` — Slow tests, skipped by `make check`, run by `make check-expensive`
- `:nativecomp` — Requires native compilation support
- `:unstable` — Under development, run by `make check-all` only

## Running Tests

```bash
# All tests:
make check

# Tests for one file:
make -C test lisp/foo/bar-tests

# Single named test:
make -C test lisp/foo/bar-tests SELECTOR='bar-tests-basic-functionality'

# Verbose output:
make -C test lisp/foo/bar-tests 2>&1 | tee test-output.log
```

## Best Practices

- Test behavior, not implementation details
- One assertion per logical check (multiple `should` in one test is fine for a single behavior)
- Use `with-temp-buffer` for buffer-dependent tests
- Use `let` to bind dynamic variables for isolated test state
- Clean up side effects: files created, buffers opened, hooks added
- Prefer `string-match-p` over `string-match` (no match data side effects)
- Name tests: `<library>-tests-<what-is-tested>`
