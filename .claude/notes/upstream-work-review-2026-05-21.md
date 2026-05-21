# Upstream-patch work — consolidated review (2026-05-21)

Retrospective covering all upstream-patch activity on `jylhis/emacs`
from 2026-05-09 through 2026-05-20.  Supersedes the per-session
`upstream-backport-review-*.md` files for navigation purposes; the
session files remain authoritative for their own SHA lists.

## 1. Executive summary

- Window: 2026-05-09 -> 2026-05-20 (5 backport sessions).
- ~106 commits cherry-picked cumulatively from `emacs-upstream/master`
  onto `dev`; branch now ~258 commits ahead of upstream master.
- 2 Darwin patches absorbed natively as fork commits:
  `ce3be1ef1ac` (NS system-appearance hook) and `f1c1c836b3f`
  (NS undecorated-round frame parameter).
- Patch-source polling subsystem stood up: skill commit `f6f611a5824`,
  survey commit `c94bdd0c693`.
- Open work: 5 commits in "needs review", 3 failed cherry-picks,
  2 fork TODOs (local package fetching, ldefs-boot regen),
  1 verify-then-absorb (`fix-ns-x-colors.patch`).

## 2. Savannah backports -- session table

Common anchor commit: `08a22b8965ec` (2026-04-27, "Don't skip
'vc-test-src-version-diff' test").

| Date (UTC)        | Reviewed | Applied         | Skipped | Pending | Failed |
|-------------------|---------:|----------------:|--------:|--------:|-------:|
| 2026-05-09        |      146 |              18 |       - |       - |      - |
| 2026-05-09T1952   |      146 | 106 (-17 dedup) |       - |       - |      - |
| 2026-05-16T1834   |       89 |              34 |       - |       - |      - |
| 2026-05-16T1902   |       55 |   0 (review)    |       - |      40 |      - |
| 2026-05-20T1931   |       51 |              28 |      14 |       5 |      3 |

## 3. What landed on `dev` (categorised)

- **lisp bug fixes** (~28): Eglot, auth-source, newsticker, shr.el,
  hideshow, markdown-ts-mode, ERC, Tramp, vc-dir, Rmail.
- **small src/ via mergiraf** (~23): sized-type fixes, overflow
  guards, `styled_format` reshape, GCC analyzer pacification.
- **test-only** (~5): jsonrpc fixtures, process cleanup, ERC test
  isolation.
- **doc & style** (~15): Calc manual, SGML/HTML, Transient,
  markdown-ts-mode docs.
- **merged via `-X theirs`** (~8): NEWS.31 redirects, keyboard.c
  SIGINT handling, margin face introduction.

Notable substantial pulls:

- `b36a26bb3b81` markdown-ts-mode improvements (+6595 lines including
  new `lisp/textmodes/markdown-ts-mode-x.el`).
- `046db6404426` format-spec now runs in caller's buffer.
- GTK3 child-frame series (8 commits) -- X11-focused, NS-tested.

## 4. What was skipped (and why)

- **autotools** (7 commits): version bumps, release-branch cuts.
  Fork removed autotools at `313f867`; Meson-only.
- **admin/** (7 commits): docs conventions, MAINTAINERS edits,
  ChangeLog churn -- not maintained by this fork.

## 5. Open savannah work

### Pending review (5)

- `1fae14a022f8` Streamline styled_format aux allocation (src/, 35 lines)
- `efb83df33142` Don't trust RLIMIT_NOFILE in process.c (115 lines)
- `389874c533bb` Eglot: unbreak for treesit-less builds
- `28a13b01c7d7` vc-refresh-state: override default-directory
- `e381cf1fc97f` Allow child processes to continue after EPIPE (135 lines)

### Failed cherry-picks (3)

- `24f9e6a69362` styled_format igc-compat -- conflict `src/editfns.c`
- `d4cb550dba6c` "; Improve last change" -- conflict
  `test/src/process-tests.el`
- `c80d22dcfcc3` Remove stray inrange_pipe comment -- conflict
  `src/process.c`

All three cluster around the process / editfns area; resolve as a
group before the next sync run.

## 6. Darwin / packaging patch absorption

| Source                        | Tracker note                  | Status |
|-------------------------------|-------------------------------|--------|
| homebrew-emacs-plus           | fork-homebrew-emacs-plus.md   | 2 of 3 absorbed; `fix-ns-x-colors.patch` = verify-then-absorb |
| nix-darwin-emacs              | fork-nix-darwin-emacs.md      | re-hosts emacs-plus patches; verdicts inherited |
| MacPorts (`editors`, `aqua`)  | fork-macports.md              | mostly defer / not-applicable (PATH injection, launchd-dbus, tree-sitter 0.26 compat) |
| emacs-mac-port (Yamamoto)     | fork-emacs-mac-port.md        | parallel codebase, reference only |
| Aquamacs                      | fork-aquamacs.md              | ~40 Elisp overlay + 11 NSSpellChecker primitives; NSSpellChecker deferred |
| nix-emacs-overlay             | fork-nix-emacs-overlay.md     | only native-comp-driver-options patch; nothing to absorb |

Absorbed into source (commits on `dev`):

- `ce3be1ef1ac` NS: `ns-system-appearance-change-functions` hook
  (KVO observer on `NSApp` effective appearance; macOS 10.14+;
  co-author Boris Buliga).
- `f1c1c836b3f` NS: `undecorated-round` frame parameter
  (NSFullSizeContentViewWindowMask; co-author Nicolas G. Querol).

## 7. Patch-source poll infrastructure

- Skill commit `f6f611a5824` adds the patch-source poll step.
- Survey commit `c94bdd0c693` audits all six patch repos and assigns
  initial verdicts.
- Baseline state:
  `.claude/skills/upstream-commit-review/scripts/state/patch-sources.json`
  (SHA-256 per `.patch` file + verdict).
- Verdicts: `absorb-now` / `verify-then-absorb` / `defer` /
  `not-applicable`.

## 8. Outstanding fork TODOs (from fork-todos.md)

1. **Local package fetching.** Externally-maintained packages
   (transient, eldoc, Tramp, Org, Eglot, ERC, Gnus, ...) currently
   ride in via savannah cherry-pick cadence.  Open intent: build a
   fork-local manifest under `admin/` with a `just` recipe to pull
   each package from its own upstream, regenerating the in-tree copy
   and recording the upstream SHA independently of GNU Emacs.
2. **Local `ldefs-boot.el` regen.** Post-Meson cutover (`313f867`)
   removed the autotools `make autoloads-force` path; the fork still
   re-syncs `lisp/ldefs-boot.el` by cherry-picking upstream's
   periodic "Update ldefs-boot.el." commits.  Add a Meson target or
   `just` helper that drives `loaddefs-generate--emacs-batch` so the
   file regenerates from the current local `lisp/` tree.

## 9. Recommended next actions

1. Resolve the 3 failed cherry-picks as a single sweep -- they share
   a code area (`src/process.c` family + `src/editfns.c`).
2. Land or reject the 5 "needs review" commits to clear backlog
   before the next sync.
3. Decide on `fix-ns-x-colors.patch` -- verify-then-absorb has been
   outstanding while the other two NS patches went through.
4. Pick up `ldefs-boot` regen first of the two fork-TODOs; it is the
   smaller piece and unblocks every future sync run.

## References

- Per-session reports: `.claude/notes/upstream-backport-review-*.md`
- Fork trackers: `.claude/notes/fork-*.md`
- Skill: `.claude/skills/upstream-commit-review/SKILL.md`
- Latest pointer: `.claude/notes/upstream-backport-review-latest.md`
