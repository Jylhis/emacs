---
description: Review code changes in the GNU Emacs codebase. Works with diffs, patches, or branch comparisons.
argument-hint: <branch-or-path>
---

# Emacs Code Review

## Diff to Review

!`git diff $ARGUMENTS 2>/dev/null || echo "No arguments provided — review staged changes or specify a branch/path."`

## Process

1. **Understand the change** — Read the diff, commit messages, and any referenced bug reports (Bug#NNNNN)
2. **Read surrounding context** — Examine the full functions and modules affected, not just the diff hunks
3. **Evaluate across dimensions**:
   - **Correctness**: Edge cases, error handling, type checking (CHECK_* macros in C, type predicates in Elisp)
   - **Conventions**: GNU coding style, naming prefixes, docstrings, lexical-binding
   - **Tests**: Are new/modified behaviors covered by ERT tests?
   - **Documentation**: Docstrings updated? `etc/NEWS` entry needed? Manual updates?
   - **Commit message**: Follows ChangeLog format? Bug references? Present tense?
   - **Compatibility**: Does the change break existing behavior or public API?
   - **Performance**: Especially in display code (xdisp.c) and tight loops
4. **Categorize findings**:
   - **Must-fix**: Bugs, data loss, security issues, crashes
   - **Should-fix**: Convention violations, missing tests, missing docs
   - **Nit**: Style preferences, minor improvements
5. **Acknowledge strengths**: Call out clean solutions and thoughtful design

## Emacs-Specific Checks

### For Elisp Changes
- [ ] `lexical-binding` enabled in file header
- [ ] All public symbols properly prefixed
- [ ] Docstrings present and pass `checkdoc`
- [ ] `defcustom` has `:type`, `:version`, `:group`
- [ ] Autoload cookies on user-facing commands
- [ ] `etc/NEWS` entry for user-visible changes
- [ ] ERT tests added or updated

### For C Changes
- [ ] `CHECK_*` macros for argument validation in DEFUNs
- [ ] GC safety (no raw pointers across GC points)
- [ ] `maybe_quit()` in long loops
- [ ] Proper error signaling (not C-level abort)
- [ ] Matching tests in `test/src/`

### For Documentation Changes
- [ ] Texinfo markup correct (run `make info` to verify)
- [ ] Index entries (`@findex`, `@vindex`) for new symbols
- [ ] Cross-references to related nodes

## Output Format

Group findings by severity. For each finding:
- File and line reference
- What the problem is
- Suggested fix (with code if applicable)

End with verdict: **ship it**, **ship with fixes**, or **rethink approach**.
