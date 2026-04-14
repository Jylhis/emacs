# GNU Emacs — Claude Code Project Guide

## What This Is

GNU Emacs source repository (version 31.0.50, development branch).
A self-documenting, extensible, real-time display editor written in C and Emacs Lisp.

## Tech Stack

- **Core**: C (src/), Emacs Lisp (lisp/)
- **Build**: Autoconf, GNU Make
- **Tests**: ERT (Emacs Lisp Regression Testing)
- **Docs**: Texinfo (doc/)
- **Platforms**: GNU/Linux, macOS, Windows, Android

## Project Structure

```
src/          C source — editor engine, display, GC, bytecode VM
lisp/         Emacs Lisp — modes, packages, UI, stdlib
test/         ERT test suite (mirrors lisp/ and src/ structure)
doc/          Texinfo manuals (emacs/, lispref/, lispintro/, misc/)
lib/          Gnulib portability library
lib-src/      Helper executables (etags, emacsclient, etc.)
admin/        Release tools, notes, developer docs
etc/          Data files, NEWS, tutorials, images
nextstep/     macOS/GNUstep build support
java/         Android build support
```

## Build Commands

```bash
# First time from repo checkout:
./autogen.sh && ./configure && make -j$(nproc)

# Bootstrap (clean rebuild):
make bootstrap

# Quick rebuild after changes:
make

# Debug-friendly build:
make configure="CFLAGS='-O0 -g3' --enable-checking=all"
```

## Test Commands

```bash
# Full test suite:
make check

# Including expensive tests:
make check-expensive

# Single file (e.g., lisp/files.el):
make -C test files-tests

# Build + test workflow:
make && make -C test foo-tests
```

## Key Conventions

- American English ("behavior" not "behaviour"), two spaces between sentences
- Elisp: `lexical-binding: t` in all new files, 80-char lines, `lisp-case` naming
- C: GNU style, `CHECK_*` macros for DEFUN argument validation
- Tests: ERT in `test/`, mirrors source structure, `:tags '(:expensive-test)` for slow tests
- Docs: update `etc/NEWS` for user-visible changes, Texinfo with index entries
- Commit messages: ChangeLog format, present tense, 50-char summary, `(Bug#NNNNN)` refs

See `.claude/rules/` for detailed path-specific coding rules.

## Key References

- @CONTRIBUTE — Full contributor guide
- `INSTALL` / `INSTALL.REPO` — Build instructions
- `admin/notes/` — Developer notes (git-workflow, bug-triage, etc.)
- `test/README` — Test suite documentation
- `etc/NEWS` — User-visible changes (update when adding features)
