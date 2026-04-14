---
description: Find the root cause of issues in GNU Emacs. No guessing, no shotgun fixes.
argument-hint: <error-or-symptom>
---

# Emacs Debugging

## Process

1. **Gather symptoms** — Collect error messages, backtraces, reproduction steps, and the gap between expected and actual behavior
2. **Form a hypothesis** — State a specific, testable theory about what is wrong
3. **Trace the code** — Read relevant source and follow the execution path toward the failure
4. **Test the hypothesis** — Use concrete evidence (logs, tests, code analysis). If evidence contradicts, reformulate
5. **Propose a fix** — Explain what to change and why it addresses the root cause

## Debugging Elisp

```elisp
;; Enable debug-on-error for backtrace:
(setq debug-on-error t)

;; Instrument a function for Edebug:
;; Place point inside defun, then M-x edebug-defun
;; Call the function — Edebug steps through it

;; Trace function calls:
(trace-function 'suspect-function)
;; ... reproduce the problem ...
(untrace-all)

;; Check byte-compilation warnings (often reveal bugs):
;; M-x byte-compile-file RET path/to/file.el RET
```

## Debugging C Core

```bash
# Build with debug symbols:
./configure CFLAGS='-O0 -g3' --enable-checking=all
make

# Run under GDB:
gdb --args src/emacs -Q

# Useful GDB commands for Emacs:
# xbacktrace        — Lisp-level backtrace
# xtype obj          — Show type of Lisp_Object
# xprint obj         — Pretty-print Lisp_Object
# pp obj             — Alias for xprint
# break Fsignal      — Break on Lisp errors
# break terminate_due_to_signal  — Break on fatal signals
```

Source `.gdbinit` from the Emacs source dir for these commands.

## Debugging Test Failures

```bash
# Run a specific failing test with verbose output:
make -C test lisp/failing-tests SELECTOR='test-name'

# Run interactively inside Emacs:
# M-x ert RET test-name RET
# Press 'b' on a failed test for backtrace
# Press 'l' for the messages log
```

## Rules

- A fix requires an identified root cause; uncertainty is acceptable, random fixes are not
- Every fix must include a regression test that fails without the fix and passes with it
- After three failed hypotheses, report what has been eliminated and ask for guidance

## Required Output

- **Root cause**: The actual problem, with evidence
- **Fix**: What to change and why
- **Regression test**: An ERT test preventing recurrence
