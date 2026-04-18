---
paths:
  - "doc/**/*.texi"
  - "etc/NEWS"
---

# Documentation Rules

## Language

- American English ("behavior" not "behaviour")
- Two spaces between sentences
- "Point" is a proper name (no article): "Point moves" not "The point moves"
- Active voice preferred: "This does not move point" not "Point is not moved by this"
- Write `Emacs's` not `Emacs'`

## Texinfo

- Use `@findex` for function/command index entries
- Use `@vindex` for variable index entries
- Use `@kindex` for key binding index entries
- Cross-reference with `@xref`, `@pxref`, `@ref`
- Verify with `make info` before committing

## NEWS Entries

- Add entry in `etc/NEWS` for user-visible changes
- Start with a summary sentence that fits one line (for Outline mode)
- Mark with `+++` if all documentation updates are done
- Mark with `---` if no documentation updates are needed
- Leave unmarked if documentation updates are still pending
- Document default values for new `defcustom` options
- Quote symbols with `'like-this'` (makes them clickable in Emacs); `t` and `nil` unquoted
- Function arguments in UPPERCASE, unquoted
- Lisp forms on own line: not quoted, indented 4 spaces
- File and program names in "double quotes"
- Manual references: `"(elisp) Documentation Tips"` format
- Validate with `emacs-news-view-mode` before pushing (symbols should be clickable)
