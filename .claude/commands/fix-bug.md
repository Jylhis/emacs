---
argument-hint: <Bug#NNNNN or description>
---

Fix the specified Emacs bug.

## Bug Context

!`echo "$ARGUMENTS" | grep -qE '^[0-9]+$' && echo "Bug#$ARGUMENTS — search debbugs.gnu.org for details" || echo "Description: $ARGUMENTS"`

## Steps

1. Reproduce or understand the bug from the description
2. Trace the code to find the root cause
3. Implement the fix with minimal changes
4. Write a regression test in the appropriate `test/` file
5. Verify: `make && make -C test <relevant>-tests`
6. Update docstrings if behavior changed
7. Add `etc/NEWS` entry if user-visible

## Commit Format

```
Fix <summary> (Bug#NNNNN)

* path/to/file.el (function-name): Describe the fix.
```
