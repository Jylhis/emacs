---
description: Write and run ERT tests for GNU Emacs changes.
argument-hint: <file-or-test-name>
---

# Emacs Testing

## File Convention

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

## Assertions

```elisp
(should FORM)                              ; FORM must be non-nil
(should-not FORM)                          ; FORM must be nil
(should-error FORM :type 'error-symbol)    ; FORM must signal error
```

## Tags

- `:expensive-test` -- slow tests, skipped by `make check`, run by `make check-expensive`
- `:nativecomp` -- requires native compilation
- `:unstable` -- under development, run by `make check-all` only

## Running

```bash
make check                                                  # all tests
make -C test lisp/foo/bar-tests                            # one file
make -C test lisp/foo/bar-tests SELECTOR='test-name'       # one test
```

Do not use `make -j` for tests (parallel test runs cause flaky failures).

## Best Practices

- Test behavior, not implementation details
- Use `with-temp-buffer` for buffer-dependent tests
- Clean up side effects: files, buffers, hooks
- Name tests: `<library>-tests-<what-is-tested>`
