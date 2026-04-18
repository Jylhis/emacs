---
description: Find the root cause of issues in GNU Emacs. No guessing, no shotgun fixes.
argument-hint: <error-or-symptom>
---

# Emacs Debugging

## Process

1. **Gather symptoms** -- error messages, backtraces, reproduction steps, expected vs actual
2. **Form a hypothesis** -- a specific, testable theory about what is wrong
3. **Trace the code** -- read relevant source, follow execution toward the failure
4. **Test the hypothesis** -- use concrete evidence; reformulate if contradicted
5. **Propose a fix** -- explain what to change and why it addresses the root cause

## Debugging Elisp

```elisp
;; Get a backtrace on error:
(setq debug-on-error t)

;; Step through a function with Edebug:
;; Place point inside defun, then C-u C-M-x (or M-x edebug-defun)
;; Call the function -- Edebug steps through it

;; Trace function calls:
(trace-function 'suspect-function)
;; ... reproduce the problem ...
(untrace-all)
```

## Debugging C Core

Build with debug symbols (per `etc/DEBUG`):
```bash
./configure --enable-checking='yes,glyphs' CFLAGS='-O0 -g3'
make
```

Run under GDB from `src/` (loads `.gdbinit` automatically):
```bash
cd src && gdb --args ./emacs -Q
```

GDB commands defined in `src/.gdbinit`:
- `xbacktrace` -- Lisp-level backtrace
- `xtype OBJ` -- show type of Lisp_Object
- `xprint OBJ` / `pp OBJ` -- pretty-print Lisp_Object
- `break Fsignal` -- break on any Lisp error
- `break terminate_due_to_signal` -- break on fatal signals

## Debugging Test Failures

```bash
# Run a failing test with output:
make -C test lisp/failing-tests SELECTOR='test-name'

# Inside Emacs:
# M-x ert RET test-name RET
# Press 'b' on a failed test for backtrace
# Press 'l' for the *Messages* log
```

## Rules

- A fix requires an identified root cause
- Every fix must include a regression test that fails without the fix and passes with it
- After three failed hypotheses, report what has been eliminated

## Output

- **Root cause**: the actual problem, with evidence
- **Fix**: what to change and why
- **Regression test**: an ERT test preventing recurrence
