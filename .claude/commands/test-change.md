---
argument-hint: <file-path>
---

Build and test changes to the specified file.

## Changed File

!`git diff --name-only HEAD 2>/dev/null || echo "$ARGUMENTS"`

## Steps

1. Identify the test file for the changed source
   - `lisp/foo.el` → `test/lisp/foo-tests.el`
   - `src/foo.c` → `test/src/foo-tests.el`
2. Build: `make -j$(nproc)`
3. Run the specific tests: `make -C test <name>-tests`
4. If infrastructure change, find affected tests: `grep -Rl <function-name> test --include="*.el"`
5. Report results: pass/fail count, any new warnings
