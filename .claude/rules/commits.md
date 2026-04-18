# Commit Message Rules

## Format

```
Summary line (50 chars or fewer, no trailing period)

Optional paragraph explaining rationale.
* path/to/file.el (function-name): Describe what changed.
* path/to/other-file.c (other_function): Describe what changed.
```

## Requirements

- Present tense: "Add feature" not "Added feature"
- Summary line: no leading whitespace, no trailing period
- Second line must be blank
- Single-line commits must end with a period
- ChangeLog entry lines: max 78 characters (63 preferred), enforced by commit hook
- Single word exception: up to 140 characters
- Reference bugs as `(Bug#NNNNN)`
- American English, complete sentences in ChangeLog entries
- Two spaces between sentences
- Prefer `https:` over `http:` in URLs
- No "Signed-off-by:" lines
- Only printable UTF-8 characters
- Lines starting with `"; "` are omitted from generated ChangeLog (use for minor commits)

## Commit Hook Enforcement

Commits are rejected if:
- Empty message or first line starts with whitespace
- Second line is not blank
- Any line exceeds 79 characters (single-word exception: 140)
- Contains "Signed-off-by:" tags
- New filenames start with `-` or have non-ASCII characters
- Unresolved merge conflict markers present
- Trailing whitespace or SPC immediately followed by TAB in indentation
