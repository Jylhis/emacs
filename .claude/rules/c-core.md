---
paths:
  - "src/**/*.c"
  - "src/**/*.h"
---

# C Core Rules

## Style

- GNU C coding style: 2-space indentation, braces on own line for functions
- Space before parentheses in calls: `foo (arg1, arg2)`
- Pointer declarations: `Lisp_Object *ptr`

## Lisp Object Handling

- Use `CHECK_*` macros to validate DEFUN arguments: `CHECK_STRING (arg)`
- Use type predicates: `STRINGP`, `CONSP`, `NILP`, `FIXNUMP`
- Extract values with: `XCAR`, `XCDR`, `XFIXNUM`, `SSDATA`

## DEFUN Format

```c
DEFUN ("name", Fname, Sname, MIN_ARGS, MAX_ARGS, INTERACTIVE,
       doc: /* Docstring mentioning ARG in UPPERCASE.  */)
  (Lisp_Object arg)
{
  CHECK_STRING (arg);
  return result;
}
```

Register with `defsubr (&Sname);` in the file's `syms_of_*` function.

## GC Safety

- Never hold raw C pointers to Lisp data across potential GC points
- Use `record_unwind_protect` for cleanup
- Call `maybe_quit ()` in long loops to allow user interrupts
- Use `AUTO_STRING` for temporary Lisp strings from C string literals

## Error Handling

- Use `signal_error`, `error`, or `xsignal2` — never C-level `abort`
- Validate arguments at function entry with `CHECK_*` macros
