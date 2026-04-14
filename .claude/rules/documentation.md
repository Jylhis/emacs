---
paths:
  - "doc/**/*.texi"
---

# Documentation Rules

## Texinfo Format

- Use `@findex` for function/command index entries
- Use `@vindex` for variable index entries
- Use `@kindex` for key binding index entries
- Cross-reference with `@xref`, `@pxref`, `@ref`

## Style

- American English ("behavior" not "behaviour")
- Two spaces between sentences
- Verify with `make info` or `makeinfo` before committing

## NEWS Entries

- Add entry in `etc/NEWS` for user-visible changes
- Start with a summary sentence that fits one line (for Outline mode)
- Mark with `+++` if all documentation updates are done
- Mark with `---` if no documentation updates are needed
- Document default values for new `defcustom` options
