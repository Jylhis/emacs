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
   - Start with a summary sentence that fits on one line (for Outline mode)
   - Document default values for new `defcustom` options
   - Mark with `+++` if all doc updates are done
   - Mark with `---` if no doc updates needed
   - Leave unmarked if doc updates are still pending
4. Use present tense and American English

Change to document: $ARGUMENTS
