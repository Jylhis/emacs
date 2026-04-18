---
description: Review code changes in the GNU Emacs codebase. Works with diffs, patches, or branch comparisons.
argument-hint: <branch-or-path>
---

# Emacs Code Review

## Diff to Review

!`git diff $ARGUMENTS 2>/dev/null || echo "No arguments provided -- review staged changes or specify a branch/path."`

## Process

1. **Understand the change** -- read the diff, commit messages, and any referenced bug reports (Bug#NNNNN)
2. **Read surrounding context** -- examine the full functions and modules affected
3. **Evaluate** against the checks below
4. **Categorize findings**: must-fix (bugs, crashes, data loss), should-fix (conventions, missing tests), nit (style)
5. **Acknowledge strengths** -- call out clean solutions

## Elisp Checks

- [ ] `lexical-binding: t` in file header
- [ ] All public symbols properly prefixed with library name
- [ ] Docstrings present, pass `checkdoc`, fill column 72
- [ ] Two spaces between sentences in docstrings and comments
- [ ] `defcustom` has `:type`, `:version`, `:group`
- [ ] Autoload cookies on user-facing commands
- [ ] `etc/NEWS` entry for user-visible changes (with `'symbol'` quoting)
- [ ] ERT tests added or updated
- [ ] Byte-compiles without warnings
- [ ] Indentation uses spaces, not tabs

## C Checks

- [ ] GNU style, tabs for indentation
- [ ] `CHECK_*` macros for DEFUN argument validation
- [ ] No raw C pointers held across GC-triggering calls
- [ ] `maybe_quit ()` in long loops
- [ ] `record_unwind_protect` for cleanup (not GCPRO, which is removed)
- [ ] Error signaling via `signal_error`/`error`/`xsignal`, not `abort`
- [ ] Two spaces between sentences in doc: comments

## Documentation Checks

- [ ] Texinfo markup correct (`make info` to verify)
- [ ] Index entries (`@findex`, `@vindex`, `@kindex`) for new symbols
- [ ] American English, "Point" without article, active voice
- [ ] NEWS symbols quoted with `'like-this'` (clickable in Emacs)

## Commit Message Checks

- [ ] Summary line under 50 chars, no trailing period, present tense
- [ ] ChangeLog entry lines under 78 chars (63 preferred)
- [ ] Bug references as `(Bug#NNNNN)`
- [ ] No "Signed-off-by:" lines

## Output

Group findings by severity with file:line references.  End with verdict: **ship it**, **ship with fixes**, or **rethink approach**.
