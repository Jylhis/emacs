---
description: Work with the C source code that implements the Emacs core (src/ directory). Auto-invoked when working with C files in src/.
user-invocable: false
---

# Emacs C Core Development

## Architecture

- **Lisp interpreter**: eval, data types, garbage collector (`eval.c`, `alloc.c`, `data.c`)
- **Buffer engine**: text storage, gap buffer, overlays (`buffer.c`, `insdel.c`)
- **Display engine**: redisplay, terminal/GUI rendering (`xdisp.c`, `dispnew.c`)
- **Window system**: frame and window management (`window.c`, `frame.c`)
- **Process management**: subprocesses, networking (`process.c`)
- **Keyboard/input**: command loop, key handling (`keyboard.c`, `cmds.c`)

## Style

- GNU C style with tabs (`indent-tabs-mode: t`, tab-width 8)
- Braces on their own line for function definitions
- Space before parentheses in calls: `foo (arg1, arg2)`
- Fill column: 72
- Two spaces between sentences in comments and doc strings

## DEFUN

```c
DEFUN ("my-function", Fmy_function, Smy_function, 1, 2, 0,
       doc: /* Short description of my-function.
First argument ARG1 is required.
Optional second argument ARG2 defaults to nil.  */)
  (Lisp_Object arg1, Lisp_Object arg2)
{
  CHECK_STRING (arg1);
  if (NILP (arg2))
    arg2 = Qnil;
  /* implementation */
  return result;
}
```

- Register in `syms_of_*` function with `defsubr (&Smy_function);`
- Argument names in doc: UPPERCASE

## Lisp Object API

```c
/* Type predicates */
STRINGP (obj)   CONSP (obj)    NILP (obj)
FIXNUMP (obj)   SYMBOLP (obj)  VECTORP (obj)
BUFFERP (obj)   FLOATP (obj)   MARKERP (obj)

/* Argument validation (signal error if wrong type) */
CHECK_STRING (arg)    CHECK_LIST (arg)     CHECK_FIXNUM (arg)
CHECK_SYMBOL (arg)    CHECK_BUFFER (arg)   CHECK_VECTOR (arg)

/* Value extraction */
XCAR (cons)           XCDR (cons)
XFIXNUM (fixnum)      XFLOAT_DATA (float)
SSDATA (string)       SCHARS (string)      SBYTES (string)
AREF (vector, idx)    ASIZE (vector)
```

## GC Safety

GCPRO is removed.  Modern Emacs uses:
- `record_unwind_protect` / `record_unwind_protect_ptr` for cleanup
- `specpdl` for dynamic bindings
- Never hold raw C pointers to Lisp data across calls that can trigger GC
- Call `maybe_quit ()` in long loops

## Build and Debug

```bash
# Debug build (from etc/DEBUG):
./configure --enable-checking='yes,glyphs' CFLAGS='-O0 -g3'
make

# Rebuild after C changes:
make -j$(nproc)

# Run under GDB (from src/ directory for .gdbinit):
cd src && gdb --args ./emacs -Q

# Key GDB commands (from src/.gdbinit):
# xbacktrace     -- Lisp-level backtrace
# xtype OBJ      -- show Lisp_Object type
# xprint OBJ     -- pretty-print Lisp_Object
# pp OBJ         -- alias for xprint
# break Fsignal  -- break on Lisp errors
# break terminate_due_to_signal  -- break on fatal signals
```

## Key Files

- `src/lisp.h` -- Lisp_Object type, macros, CHECK_* definitions
- `src/eval.c` -- Lisp evaluator
- `src/alloc.c` -- Allocator and garbage collector
- `src/xdisp.c` -- Display engine (extensively commented)
- `src/keyboard.c` -- Command loop and input
