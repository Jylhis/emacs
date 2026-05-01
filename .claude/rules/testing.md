---
paths:
  - "test/**/*.el"
---

# Testing Rules

## File Convention

Tests for `lisp/foo/bar.el` go in `test/lisp/foo/bar-tests.el`.
Tests for `src/eval.c` go in `test/src/eval-tests.el`.

## Test Structure

```elisp
(ert-deftest bar-tests-basic-functionality ()
  "Verify bar-do-thing handles normal input."
  (should (equal (bar-do-thing "input") "expected")))
```

## Tags

- Tag slow tests: `:tags '(:expensive-test)`
- Tag native-comp tests: `:tags '(:nativecomp)`
- Tag unstable tests: `:tags '(:unstable)`

## Running

- Single file: `make -C test lisp/foo/bar-tests`
- Single test: `make -C test lisp/foo/bar-tests SELECTOR='test-name'`
- All tests: `make check`

Do not use `make -j` for tests -- parallel test runs cause flaky failures.

## Best Practices

- Use `with-temp-buffer` for buffer-dependent tests
- Clean up side effects (files, buffers, hooks)
- Name tests: `<library>-tests-<what-is-tested>`
