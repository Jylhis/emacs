# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

GNU Emacs source repository (version 31.0.50, development branch).
C and Emacs Lisp codebase. See @CONTRIBUTE for the full contributor guide.

## Project Structure

```
src/          C source -- editor engine, Lisp interpreter, display, GC, bytecode VM
lisp/         Emacs Lisp -- modes, packages, UI, standard library
test/         ERT test suite (mirrors lisp/ and src/ structure)
doc/          Texinfo manuals (emacs/, lispref/, lispintro/, misc/)
lib/          Gnulib portability library
lib-src/      Helper executables (etags, emacsclient, etc.)
admin/        Release tools, developer notes (see admin/notes/)
etc/          Data files, NEWS, tutorials, images, DEBUG guide
```

## Build

This branch's only supported build system is Meson + Ninja.  The
autotools entry points (configure.ac, autogen.sh, every Makefile.in,
GNUmakefile, make-dist) were removed at the phase-10 cutover commit
`313f867`; see `.claude/notes/build-system.md` for the post-cutover
parity audit and the work that follows.

```bash
meson setup build -Dnative-compilation=yes
meson compile -C build                              # full build
meson test -C build --suite smoke                   # ERT smoke tests
meson install -C build --destdir=/tmp/stage         # staged install
```

Debug build (recommended for development, per etc/DEBUG):
```bash
meson setup build --buildtype=debug \
  -Dcheck=yes,glyphs -Dcheck-lisp-object-type=true
```

## Test

```bash
meson test -C build                # all registered tests
meson test -C build --suite smoke  # smoke set only
meson test -C build NAME           # one test by name
```

`meson test` defaults to a single worker; force a higher count
explicitly only when you've verified the test in question is
parallel-safe (`--num-processes N`).

## Key Conventions

- American English ("behavior" not "behaviour"), two spaces between sentences
- Fill column: 72 for all code and docstrings
- "Point" is a proper name (no article): "Move point" not "Move the point"
- Elisp: spaces only, `lexical-binding: t`
- C: GNU style with tabs, tab-width 8
- Tests: ERT in `test/` mirroring source paths
- Docs: update `etc/NEWS` for user-visible changes
- Commits: ChangeLog format, present tense, 50-char summary

See `.claude/rules/` for detailed path-specific rules.

## Research Notes

Investigative notes live in `.claude/notes/`.  When exploring the
repository documentation, build system, or developer tooling, update
the relevant note file (or create a new one) so findings persist
across sessions.  See `.claude/notes/README.md` for the index.

## Debugging

GDB from `src/` directory (loads `.gdbinit` automatically):
```bash
cd src && gdb --args ./emacs -Q
```

Key GDB commands from `src/.gdbinit`: `xbacktrace` (Lisp backtrace), `xtype OBJ`, `xprint OBJ`/`pp OBJ`, `break Fsignal` (break on Lisp errors).

Elisp debugging: `(setq debug-on-error t)` for backtraces, `C-u C-M-x` to instrument with Edebug.

## External Resources

- Bug tracker: https://debbugs.gnu.org
- Mailing list: emacs-devel@gnu.org
- Report bugs: `M-x report-emacs-bug` or email bug-gnu-emacs@gnu.org
