# Emacs C Core Development

Work with the C source code that implements the Emacs core (src/ directory).

## When to Use

Automatically loaded when working with `.c` or `.h` files in the `src/` directory.

## Architecture Overview

The C core implements:
- **Lisp interpreter**: eval, data types, garbage collector (`eval.c`, `alloc.c`, `data.c`)
- **Buffer engine**: text storage, gap buffer, overlays (`buffer.c`, `insdel.c`)
- **Display engine**: redisplay, terminal/GUI rendering (`xdisp.c`, `dispnew.c`)
- **Window system**: frame and window management (`window.c`, `frame.c`)
- **Process management**: subprocesses, networking (`process.c`)
- **Keyboard/input**: command loop, key handling (`keyboard.c`, `cmds.c`)

## Coding Style

### GNU C Style
- Indent with spaces (2-space default in GNU style)
- Braces on their own line for function definitions
- Space before parentheses in function calls: `foo (arg1, arg2)`
- No space after cast: `(int)value`
- Pointer declarations: `Lisp_Object *ptr`

### Lisp Object Handling

```c
/* All Lisp values are Lisp_Object — a tagged pointer/integer */
Lisp_Object val = XCAR (list);       /* Extract car of a cons */
CHECK_STRING (arg);                    /* Signal error if not a string */
EMACS_INT n = XFIXNUM (number);       /* Extract fixnum value */

/* Type checking macros */
STRINGP (obj)    /* Is it a string? */
CONSP (obj)      /* Is it a cons cell? */
NILP (obj)       /* Is it nil? */
FIXNUMP (obj)    /* Is it a fixnum? */
```

### Defining Lisp Primitives (DEFUN)

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
- Document with `doc:` comment using Texinfo-like markup
- Argument names in doc: UPPERCASE

### Memory and GC Safety

- Use `GCPRO` / `record_unwind_protect` for GC roots when needed
- Call `maybe_quit ()` in long loops to allow user interrupts
- Use `AUTO_STRING` for temporary Lisp strings from C literals
- Never hold raw C pointers to Lisp data across potential GC points

### Error Handling

```c
signal_error ("Description", data);       /* Signal a generic error */
error ("Format string %s", cstr);          /* Signal with message */
xsignal2 (Qwrong_type_argument, Qstringp, obj);  /* Type error */
```

## Build and Test

```bash
# Rebuild after C changes:
make -j$(nproc)

# Debug build:
./configure CFLAGS='-O0 -g3' --enable-checking=all
make

# Run C-level tests:
make -C test check-src

# Run Emacs under GDB:
gdb --args src/emacs -Q
```

## Key Files

- `src/lisp.h` — Core Lisp_Object type definitions and macros
- `src/eval.c` — Lisp evaluator
- `src/alloc.c` — Memory allocation and garbage collector
- `src/xdisp.c` — Display/redisplay engine (largest file)
- `src/keyboard.c` — Command loop and input handling
- `src/emacs.c` — Main entry point and initialization
