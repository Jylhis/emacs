---
argument-hint: <description of change>
---

Add an etc/NEWS entry for a user-visible change.

## Recent Changes

!`git log --oneline -5`

## Instructions

1. Read `etc/NEWS` to understand the current format and section headings
2. Find the appropriate section for this change
3. Add entry following these rules:
   - Start with a summary sentence that fits one line (for Outline mode)
   - Document default values for new `defcustom` options
   - Mark with `+++` if all doc updates are done
   - Mark with `---` if no doc updates needed
   - Leave unmarked if doc updates are still pending
4. Quoting conventions:
   - Symbols, keywords, single keys: `'like-this'` (makes clickable in Emacs)
   - `t` and `nil` are never quoted
   - Function arguments: UPPERCASE, unquoted
   - Lisp forms on own line: unquoted, indented 4 spaces
   - File and program names: "in double quotes"
5. Use present tense, American English, two spaces between sentences

Change to document: $ARGUMENTS
