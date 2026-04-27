---
paths:
  - "src/**/*.c"
  - "src/**/*.h"
---

# C Core Rules

## Style

- GNU C style (`c-file-style: "GNU"` in .dir-locals.el)
- Indent with tabs (`indent-tabs-mode: t`), tab-width 8
- Space before parentheses in calls: `foo (arg1, arg2)`
- Braces on their own line for function definitions
- Fill column: 72
- Two spaces between sentences in comments and doc strings

## DEFUN Format

```c
DEFUN ("name", Fname, Sname, MIN_ARGS, MAX_ARGS, INTERACTIVE,
       doc: /* Docstring.  ARG in UPPERCASE.  Two spaces after periods.  */)
  (Lisp_Object arg)
{
  CHECK_STRING (arg);
  return result;
}
```

Register with `defsubr (&Sname);` in the file's `syms_of_*` function.

## Lisp Object Handling

- Validate DEFUN arguments at entry: `CHECK_STRING`, `CHECK_LIST`, `CHECK_FIXNUM`
- Type predicates: `STRINGP`, `CONSP`, `NILP`, `FIXNUMP`, `SYMBOLP`
- Extract values: `XCAR`, `XCDR`, `XFIXNUM`, `SSDATA`, `SCHARS`

## GC Safety

- GCPRO is removed; do not use it
- Use `record_unwind_protect` for cleanup across potential GC points
- Call `maybe_quit ()` in long loops to allow user interrupts
- Use `AUTO_STRING` for temporary Lisp strings from C literals
- Never hold raw C pointers to Lisp data across GC-triggering calls

## Error Handling

- Use `signal_error`, `error`, or `xsignal2` -- never `abort`
- Validate arguments at function entry with `CHECK_*` macros
