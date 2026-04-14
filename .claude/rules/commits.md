# Commit Message Rules

## Format

```
Summary line (50 chars max, no trailing period)

Optional paragraph explaining rationale.
* path/to/file.el (function-name): Describe what changed.
* path/to/other-file.c (other_function): Describe what changed.
```

## Requirements

- Present tense: "Add feature" not "Added feature"
- Summary line: no leading whitespace, no trailing period, max 50 chars
- Second line must be blank
- ChangeLog entry lines: max 78 characters (63 preferred)
- Reference bugs as `(Bug#NNNNN)`
- American English, complete sentences in ChangeLog entries
- Prefer `https:` over `http:` in URLs
- No "Signed-off-by:" lines
- Only printable UTF-8 characters
