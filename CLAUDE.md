# GNU Emacs -- Claude Code Project Guide

## What This Is

GNU Emacs source repository (version 31.0.50, development branch).
C and Emacs Lisp.  See @CONTRIBUTE for full contributor guide.

## Project Structure

```
src/          C source -- editor engine, display, GC, bytecode VM
lisp/         Emacs Lisp -- modes, packages, UI, stdlib
test/         ERT test suite (mirrors lisp/ and src/ structure)
doc/          Texinfo manuals (emacs/, lispref/, lispintro/, misc/)
lib/          Gnulib portability library
lib-src/      Helper executables (etags, emacsclient, etc.)
admin/        Release tools, developer notes (see admin/notes/)
etc/          Data files, NEWS, tutorials, images, DEBUG
```

## Build

```bash
./autogen.sh && ./configure && make -j$(nproc)    # first time
make                                               # rebuild
make bootstrap                                     # clean rebuild
```

## Test

```bash
make check                         # full suite
make check-expensive               # include slow tests
make -C test foo-tests             # single file
make && make -C test foo-tests     # build + test
```

## Key Conventions

- American English, two spaces between sentences
- Elisp: spaces only, `lexical-binding: t`, fill column 72
- C: GNU style with tabs, fill column 72
- Tests: ERT, `:tags '(:expensive-test)` for slow tests
- Docs: update `etc/NEWS` for user-visible changes
- Commits: ChangeLog format, present tense, 50-char summary

See `.claude/rules/` for path-specific rules.
