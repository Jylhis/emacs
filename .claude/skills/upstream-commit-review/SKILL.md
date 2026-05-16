---
name: upstream-commit-review
description: Fetch new commits from GNU Emacs upstream (savannah) and triage them for backport into this fork. Auto-cherry-picks safe categories (docs, lisp bug fixes with Bug#NNNNN, lisp docstring/style fixes, test-only changes, small src/ fixes, lisp+NEWS Bug# fixes), uses mergiraf as a syntax-aware merge driver for C/C++ conflicts, and applies a bounded -X theirs retry policy for known drift files. Writes a markdown report under .claude/notes/. Use when the user asks to sync upstream, review upstream commits, or backport upstream changes.
---

# Upstream commit review

Triage commits from GNU Emacs upstream (`git.savannah.gnu.org`) for
backport into this fork.  This fork has diverged from upstream in two
relevant ways: the autotools entry points were removed at commit
`313f867` (the build is now Meson-only), and `etc/NEWS` was renamed to
`etc/NEWS.31`.  This skill applies safe upstream changes
automatically, leans on `mergiraf` and `git rerere` for conflict
resolution, and writes a markdown report listing what needs human
review.

## Invocation

```
bash .claude/skills/upstream-commit-review/scripts/apply.sh \
    [--dry-run] [--smoke] [--retry-allow=PATH,PATH,...]
```

- `--dry-run`     — print the classification TSV; do not touch HEAD.
- `--smoke`       — run `meson test -C build --suite smoke` after the batch.
- `--retry-allow` — override the tier-3 drift allowlist (defaults to
                   `src/keyboard.c,src/xdisp.c,src/coding.c,etc/AUTHORS`).

## Pre-flight (handled by `scripts/lib.sh`)

The script refuses to start unless:

1. The working tree is clean, ignoring untracked files under `.claude/`,
   `.direnv/`, `build*/`, and `node_modules/`.
2. HEAD is not detached.
3. The `emacs-upstream` remote points at
   `https://git.savannah.gnu.org/git/emacs.git`.  If the remote is
   absent, it is added; if it points elsewhere, the script aborts.
4. `git fetch emacs-upstream master` succeeds (no fallback to a stale
   ref).

The pre-flight also registers `mergiraf` as a per-file merge driver
for C/C++ files via `git config --local merge.mergiraf.*` and links
`attributes/gitattributes` into `.git/info/attributes`.

## Candidate set

The script combines two filters:

1. **Patch-id dedupe** via `git log --cherry-pick --right-only`
   (skips upstream commits whose patch-id is already in our history).
2. **Trailer-set dedupe**: SHAs parsed from `(cherry picked from
   commit ...)` trailers in our history since the merge-base.  This
   catches commits whose patch-id diverged from upstream — typically
   the result of a previous `-X theirs` retry.

Empty result ⇒ a one-line "no candidates" report and the script stops.

## Classification rules

`scripts/classify.py` implements the rule ladder.  First match wins;
all rules are unit-tested in `scripts/test_classify.py`.

| #   | Bucket            | Match                                                                 | Action     |
|-----|-------------------|-----------------------------------------------------------------------|------------|
| 1   | autotools         | any file matches `^(configure\.ac\|autogen\.sh\|make-dist\|GNUmakefile)$`, `Makefile\.in$`, `^m4/` | SKIP |
| 2   | merge-noise       | subject matches `^(; *)?Merge \b` or contains `gitmerge`              | SKIP       |
| 3   | admin             | every file under `admin/`, or matches `^ChangeLog(\.[0-9]+)?$` or `^etc/MAINTAINERS$` | SKIP |
| 3.5 | release-branch    | subject matches `^Change \w+ version for Emacs \d+ to `, `^Cut the emacs-\d+ release branch`, or `^Bump (master )?Emacs version` | SKIP |
| —   | (missing-file)    | any file in commit not present in HEAD, **excluding** files the commit adds (`A` in `--name-status`) AND with `etc/NEWS` mapped to `etc/NEWS.31` via the fork's rename table | force REVIEW |
| 4   | doc-only          | every file under `doc/`, `etc/(NEWS\|NEWS.NN\|ERC-NEWS\|HISTORY\|AUTHORS\|PROBLEMS)`, or matches `\.texi(nfo)?$`, `\.org$` | AUTO |
| 5   | test-only         | every file under `test/`                                              | AUTO       |
| 6   | lisp-bugfix       | **`Bug#` anywhere in subject or body** AND every file under `lisp/` or `test/` | AUTO       |
| 7   | lisp-doc-style    | every file matches `^lisp/.+\.el$`, `LINES < 50`, AND (subject begins with `; ` OR matches `\b(docstring\|doc fix\|typo\|when-let\|comment fix)\b`) | AUTO |
| 8   | small-src         | every file under `src/`, `LINES < 50`, AND (**`Bug#` anywhere in subject or body** OR `LINES < 20` OR subject begins with `Fix `/`; Fix `/`Pacify `/`Avoid `/`; Avoid `/`Don't `/`; * src/`) | AUTO |
| 9   | lisp+news-bug     | **`Bug#` anywhere in subject or body** AND every file under `lisp/`, `test/`, `doc/`, or `etc/NEWS(\.NN)?` | AUTO |
| 10  | review (feature)  | subject matches `^(Add\|New\|Introduce)\b`                            | REVIEW with reason `feature` |
| 11  | review            | everything else                                                       | REVIEW     |

Why-column tags for REVIEW rows: `feature`, `large`, `lisp+src`,
`lisp-multi-area`, `src-multi-file`, `lisp-no-bug`, `unclassified`,
`missing-file:<path>`, `conflict:<paths>` (set during apply, not
classification).

### Rule ladder design notes

- **`Bug#` is matched in body too.**  Many upstream commits keep
  `Bug#NNNNN` only in the trailer / body, not the subject — the
  classifier walks both.
- **Added files are not "missing".**  A commit that creates
  `test/.../new-scenario.el` shouldn't be demoted just because that
  file isn't in HEAD yet — we use `git show --name-status` and
  exclude `A` entries from the missing-file check.
- **`etc/NEWS` is rename-aware.**  Upstream's `etc/NEWS` is
  `etc/NEWS.31` in this fork; the renamed-paths map in
  `classify.py` (`RENAMED_TO`) covers this so commits touching
  `etc/NEWS` are not falsely flagged.  Git's rename detection
  routes the diff hunk during cherry-pick.
- **Release-branch commits are auto-skipped.**  Version bumps and
  release-branch cuts (e.g. `Change ERC version for Emacs 31 to
  5.6.2.31.1`) live on the `emacs-NN` release branch and travel to
  master only via merge.  The standalone commit doesn't apply to
  master-tracking forks and previously had to be hand-skipped on
  every run.

## Cherry-pick & conflict ladder

`scripts/apply.sh` walks each AUTO row through:

1. **Plain `git cherry-pick -x`.**  Mergiraf engages automatically on
   `.c` / `.h` / `.cc` / `.cpp` files thanks to the gitattributes
   registration; if it resolves the conflict, the commit lands clean.
2. **NEWS.31 redirect** — when the only conflicted file is
   `etc/NEWS.31` and the upstream commit's diff originally touched
   only `etc/NEWS`, retry with `-X theirs`.  Git's rename-detection
   has already routed the upstream hunk; the report's range-diff
   section lets a human verify section ordering.
3. **Bounded `-X theirs` retry** — when conflict files are a subset
   of the drift allowlist (`src/keyboard.c,src/xdisp.c,src/coding.c,
   etc/AUTHORS` by default), retry with `-X theirs`.
4. **Otherwise** — abort and demote to REVIEW with `conflict:<paths>`.

Full policy detail and the rationale ("prefer upstream" rule) live in
`references/conflict-resolution.md`.

`git rerere` is enabled repo-wide (`rerere.enabled=true`,
`rerere.autoupdate=true`); each manually-resolved REVIEW conflict is
remembered, so a second run after partial triage auto-resolves
recurring conflict shapes without further input.

## Report

`scripts/report.py` renders
`.claude/notes/upstream-backport-review-<TS>.md` (timestamp from
`date -u +%Y-%m-%dT%H%M`) and rewrites
`.claude/notes/upstream-backport-review-latest.md` to point at it.
Multiple runs in a single day do not overwrite each other.

Sections:

- **Summary header** — anchor SHA + date, `behind` count, all
  per-bucket counts.
- **Applied** — clean cherry-picks.
- **Retried with -X theirs** — drift / NEWS.31 redirect resolutions.
- **Needs review (grouped by area)** — `src/`, `lisp/<topic>`,
  `doc/`, `etc/`, `lib-src/`, `test/`, `other`.  Each row lists the
  Why tag.
- **Failed (cherry-pick aborted)** — the conflict path list.
- **Skipped** — autotools / admin / merge-noise.
- **Range-diffs of -X theirs resolutions** — `git range-diff`
  excerpts per retried commit, with `difft` rendering when the
  binary is on PATH.
- **NEWS hunks needing port to etc/NEWS.31** — for verification of
  rename-detected NEWS edits.

## After running

The script prints:

1. The summary counts.
2. The relative path to the report and the `latest` pointer.
3. The number of new commits on the current branch
   (`git rev-list --count "$ANCHOR"..HEAD`).
4. If any NEWS-port-required: a one-liner pointing at the report's
   NEWS-port section.
5. A reminder that nothing has been pushed.  Recommend running
   `meson test -C build --suite smoke` (or pass `--smoke` next time)
   before pushing.

When `--smoke` is passed, `apply.sh` runs `meson setup build
--reconfigure` first.  This is idempotent when nothing changed, but
necessary when the batch included a file rename or add — Meson's
lisp file manifest is captured at configure time by
`meson/list_lisp_files.py`, so a stale manifest would otherwise
break the build.

For backport-commit conventions when finalizing the merge into `dev`,
see `.claude/rules/commits.md` and `.claude/notes/git-workflow.md`.

## Guard rails

- Never push, never switch branches, never `git reset --hard`.
- Outside the codified retry tiers, never resolve conflicts; abort
  and demote to REVIEW.  If `cherry-pick --abort` itself fails,
  hard-stop with an error.
- Never delete prior reports; always write to a unique timestamped
  path.
- If `git fetch emacs-upstream master` fails, stop — do not fall back
  to a stale ref.

## Implementation map

```
scripts/lib.sh             pre-flight, remote/fetch, mergiraf wiring
scripts/classify.py        rule engine, batched git metadata gather
scripts/test_classify.py   unittest fixtures for the rule ladder
scripts/apply.sh           cherry-pick loop + tier ladder
scripts/report.py          markdown rendering, range-diff embedding
attributes/gitattributes   per-file merge driver assignments
references/conflict-resolution.md   "prefer upstream" policy detail
```

External tools used (registered in `devenv.nix`):

- `mergiraf` — tree-sitter-aware merge driver for C/C++.
- `difftastic` (`difft`) — syntax-aware diff renderer in the report.
- `git-imerge` — manual fallback for stubborn cascading conflicts;
  invoked by the user, not by the skill.

Tools considered and not used: `git replay`, `wiggle`, `diffsitter`,
`delta` — see the design notes in
`/Users/markus/.claude/plans/buzzing-puzzling-raven.md` (this
session's plan) for rationale.

## Known footguns

- `Makefile\.in$` in rule 1 would also match `lisp/Makefile.in` if
  such a path existed.  None do post-autotools-removal; be aware on
  another fork.
- `--cherry-pick --right-only` uses Git's patch-id, which normalizes
  whitespace but not diff context.  The trailer-set augment catches
  shifts that `-X theirs` retries introduce.
- Mergiraf supports C/C++ but not Emacs Lisp or Texinfo as of late
  2025.  Lisp / NEWS.31 conflicts still go through the textual
  ladder.
- This fork is NS-focused.  X11 / GTK3 changes apply cleanly on the
  source side but exercise code paths we don't routinely build —
  smoke-test before pushing.
