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
src/          C source for the Emacs core (editor engine, display, GC, bytecode VM)
lisp/         Emacs Lisp source (modes, packages, UI, Emacs Lisp stdlib)
test/         ERT test suite (mirrors lisp/ and src/ structure)
doc/          Texinfo manuals (emacs/, lispref/, lispintro/, misc/)
lib/          Gnulib portability library
lib-src/      Helper executables (etags, emacsclient, etc.)
admin/        Release tools, notes, and developer documentation
etc/          Data files, NEWS, tutorials, images
nextstep/     macOS/GNUstep build support
java/         Android build support
```

## Build Commands

```bash
# First time (from repo checkout):
./autogen.sh
./configure            # add flags as needed, e.g. --with-tree-sitter
make                   # or: make -j$(nproc)

# Bootstrap (clean rebuild):
make bootstrap

# Quick rebuild after changes:
make

# Debug-friendly build:
make configure="CFLAGS='-O0 -g3' --enable-checking=all"

# Build from clean repo checkout (shortcut):
make                   # runs autogen.sh + configure + make automatically
```

## Test Commands

```bash
# Run the full test suite:
make check

# Run expensive tests too:
make check-expensive

# Run all tests including slow/unstable:
make check-all

# Run tests for a specific file (e.g., lisp/files.el):
make -C test files-tests

# Run tests for a directory:
make -C test lisp-net

# Run a single test and see output:
make -C test lisp/files-tests
```

## Emacs Lisp Coding Conventions

### Naming
- Use `lisp-case` for all identifiers: `my-package-function-name`
- Prefix all global symbols with the package/library name: `my-pkg-variable`
- Private/internal names use `--` prefix: `my-pkg--internal-helper`
- Predicates: single-word end in `p` (`listp`), multi-word end in `-p` (`buffer-live-p`)
- Face names should NOT end in `-face`

### Style
- Enable `lexical-binding` in all new files: `;;; -*- lexical-binding: t; -*-`
- Use default Emacs indentation; do not put closing parens on separate lines
- Lines should not exceed 80 characters when feasible
- Use `when` instead of `(if x (progn ...))`, `unless` instead of `(when (not ...) ...)`
- Prefer `#'function-name` over `'function-name` for function references
- Use `(1+ x)` and `(1- x)` instead of `(+ x 1)` and `(- x 1)`

### Documentation
- Every public function/variable needs a docstring
- Docstrings start with a single imperative sentence ("Return the buffer name.")
- Mention arguments in UPPERCASE in docstrings
- Use `checkdoc` to validate docstrings before submitting
- American English preferred (e.g., "behavior" not "behaviour")
- Two spaces between sentences

### Comments
- `;;;` — file section headings
- `;;`  — code block or top-level comments
- `;`   — end-of-line margin comments

### File Structure
- First line: `;;; filename.el --- Short description  -*- lexical-binding: t; -*-`
- End with `(provide 'filename)` and `;;; filename.el ends here`
- Use `require` for dependencies, not `load`
- Add autoload cookies (`;;;###autoload`) for user-facing commands and mode definitions

## Commit Message Format

Follow the GNU Emacs ChangeLog-style commit messages:

```
Summary line (50 chars max, no trailing period)

Optional paragraph explaining rationale.
* path/to/file.el (function-name): Describe what changed.
* path/to/other-file.c (other_function): Describe what changed.
```

Rules:
- Present tense ("Add feature" not "Added feature")
- Summary line: no leading whitespace, no trailing period, max 50 chars
- Second line must be blank
- ChangeLog entry lines: max 78 characters (63 preferred)
- Reference bugs as `(Bug#NNNNN)`
- American English, complete sentences in ChangeLog entries
- Prefer `https:` over `http:` in URLs

## Testing Your Changes

- Add ERT tests for bug fixes and new functionality when possible
- Expensive tests: tag with `:tags '(:expensive-test)`
- Test file for `lisp/foo.el` goes in `test/lisp/foo-tests.el`
- Run relevant tests before committing: `make && make -C test foo-tests`
- For infrastructure changes, grep for affected functions: `grep -Rl function-name test --include="*.el"`

## Key References

- `CONTRIBUTE` — Full contributor guide
- `INSTALL` / `INSTALL.REPO` — Build instructions
- `admin/notes/` — Developer notes (git-workflow, bug-triage, documentation, etc.)
- `test/README` — Test suite documentation
- `test/file-organization.org` — Test file naming and structure
- `etc/NEWS` — User-visible changes (update when adding features)
