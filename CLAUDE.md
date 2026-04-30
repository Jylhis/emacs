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

This branch is migrating from Autotools to Meson + Ninja
(`.claude/plans/migrate-from-current-build-replicated-gadget.md`).
Both build systems coexist; the Meson tree under `meson.build` /
`meson/` is the long-term path.

Meson (preferred on this branch):
```bash
meson setup build -Dnative-compilation=yes
meson compile -C build                              # full build
meson test -C build --suite smoke                   # ERT smoke tests
meson install -C build --destdir=/tmp/stage         # staged install
```

Autotools (legacy):
```bash
./autogen.sh && ./configure && make -j$(nproc)    # first time from repo
make                                               # rebuild after changes
make bootstrap                                     # clean full rebuild
```

Debug build (recommended for development, per etc/DEBUG):
```bash
./configure --enable-checking='yes,glyphs' --enable-check-lisp-object-type CFLAGS='-O0 -g3'
```

## Test

Meson:
```bash
meson test -C build                # all registered tests
meson test -C build --suite smoke  # smoke set only
meson test -C build NAME           # one test by name
```

Autotools:
```bash
make check                                          # full suite
make check-expensive                                # include slow tests
make -C test lisp/foo/bar-tests                     # single test file
make -C test lisp/foo/bar-tests SELECTOR='test-name'  # single test
make -C test src/eval-tests                         # C source tests
```

Do not use `make -j` for tests -- parallel test runs cause flaky failures.

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
