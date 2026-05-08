---
name: upstream-commit-review
description: Fetch new commits from GNU Emacs upstream (savannah) and triage them for backport into this fork. Auto-cherry-picks safe categories (docs, lisp bug fixes with Bug#NNNNN, test-only changes, small src/ fixes) and writes a markdown report of the rest under .claude/notes/. Use when the user asks to sync upstream, review upstream commits, or backport upstream changes.
---

# Upstream commit review

Triage commits from GNU Emacs upstream (`git.savannah.gnu.org`) for
backport into this fork.  This fork has diverged from upstream in ways
that make a plain `git merge upstream/master` painful — most notably,
the autotools entry points (`configure.ac`, `autogen.sh`, `make-dist`,
all `Makefile.in`, `GNUmakefile`) were removed at commit `313f867` and
the build is now Meson-only.  This skill applies safe upstream changes
automatically and writes a markdown report listing what needs human
review.

## Pre-flight (always run first)

1. Working tree must be clean and HEAD must not be detached:
   ```bash
   git status --porcelain   # must be empty
   git symbolic-ref -q HEAD # must succeed
   ```
   If either check fails, stop and tell the user.

2. Record the current branch — every operation runs on it, no checkouts.
   ```bash
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   ```

3. Ensure the upstream remote exists *and* points at savannah.  If the
   remote already exists with a different URL (personal fork, stale
   mirror), abort — do not silently fetch and cherry-pick from the
   wrong source.
   ```bash
   EXPECTED=https://git.savannah.gnu.org/git/emacs.git
   if URL=$(git remote get-url emacs-upstream 2>/dev/null); then
       [ "$URL" = "$EXPECTED" ] || {
           echo "emacs-upstream points at $URL, expected $EXPECTED" >&2
           exit 1
       }
   else
       git remote add emacs-upstream "$EXPECTED"
   fi
   git fetch emacs-upstream master
   ```

## Determine the commit range

Use `git merge-base` to find the most recent common ancestor between
this branch and upstream — that is the sync point regardless of how
previous merges were spelled.

```bash
ANCHOR=$(git merge-base HEAD emacs-upstream/master)
```

List the commits to triage.  `--cherry-pick --right-only` skips upstream
commits whose patch-id is already in our history (typical for
long-lived forks where some changes have been backported under a
different SHA).  `--no-merges` excludes upstream's own merge commits.

```bash
git log --reverse --no-merges --cherry-pick --right-only \
        --format='%H' HEAD...emacs-upstream/master
```

If the list is empty, write a one-line "nothing to do" report and stop.

## Per-commit classification

For each commit `SHA`, gather metadata once:

```bash
SUBJECT=$(git show -s --format=%s "$SHA")
FILES=$(git show --name-only --format= "$SHA" | sed '/^$/d')
LINES=$(git show --shortstat --format= "$SHA" \
        | awk '/files? changed/ {
                 for (i=1; i<=NF; i++)
                   if ($i ~ /^[0-9]+$/ && $(i+1) ~ /(insertion|deletion)/) s += $i
               } END { print s+0 }')
```

Apply the rules **in order**, first match wins:

| # | Bucket | Match | Action |
|---|---|---|---|
| 1 | SKIP / autotools | any file matches `^(configure\.ac\|autogen\.sh\|make-dist\|GNUmakefile)$`, `Makefile\.in$`, or `^m4/` | report only |
| 2 | SKIP / merge-noise | subject matches `^(Merge \|; \* )` or `gitmerge` (upstream's own merges/noise) | report only |
| 3 | SKIP / admin churn | every file is under `admin/` or matches `^ChangeLog` | report only |
| 4 | AUTO / doc-only | every file matches `^doc/`, `^etc/NEWS`, `\.texi$`, or `\.texinfo$` | cherry-pick |
| 5 | AUTO / test-only | every file matches `^test/` | cherry-pick |
| 6 | AUTO / lisp bugfix | subject contains `Bug#` AND every file matches `^lisp/` or `^test/` | cherry-pick |
| 7 | AUTO / small C fix | every file matches `^src/`, `LINES < 50`, AND subject starts with `Fix ` or contains `Bug#` | cherry-pick |
| 8 | REVIEW | everything else | report only |

## Cherry-pick (AUTO buckets only)

```bash
if git cherry-pick -x "$SHA"; then
    NEW_SHA=$(git rev-parse HEAD)
    # record APPLIED row: SHA, NEW_SHA, SUBJECT, bucket
else
    git cherry-pick --abort
    # demote to REVIEW with reason "conflict"
fi
```

`-x` records the original SHA in the commit message so future `gitmerge`
runs can detect that the change is already present upstream.

Never resolve a conflict automatically.  Conflicts always become REVIEW
entries.

## Report

Write to `.claude/notes/upstream-backport-review-$(date -u +%Y-%m-%d).md`
(overwrite if it already exists for today).  Structure:

```markdown
# Upstream backport review — <YYYY-MM-DD>

- Anchor commit: <SHA> (<subject>)
- Range: <ANCHOR>..emacs-upstream/master
- Reviewed: <N>   Applied: <A>   Needs review: <R>   Skipped: <S>

## Applied

| Original SHA | New SHA | Subject | Bucket |
|---|---|---|---|
| ... | ... | ... | ... |

## Needs review

| SHA | Subject | Files | Why |
|---|---|---|---|
| ... | ... | ... | conflict / unclassified / large |

## Skipped

| SHA | Subject | Reason |
|---|---|---|
| ... | ... | autotools / merge-noise / admin |
```

Truncate the `Files` column to the first 5 paths followed by `…` if
longer.  Keep each table row on one line so the report stays grep-able.

## Final user message

After writing the report, print:

1. The summary counts (Reviewed / Applied / Needs review / Skipped).
2. The relative path to the report file.
3. The number of new commits now on `$BRANCH` (run
   `git rev-list --count "$ANCHOR"..HEAD`).
4. **Reminder**: nothing has been pushed.  Recommend the user run
   `meson test -C build --suite smoke` before pushing, and inspect each
   cherry-picked commit (`git log --oneline "$ANCHOR"..HEAD`).
5. Point at `.claude/rules/commits.md` and `.claude/notes/git-workflow.md`
   for backport conventions if the user plans to merge to `dev`.

## Guard rails

- Never push, never switch branches, never `git reset --hard`.
- Never resolve conflicts; always abort and demote to REVIEW.
- Never delete previously generated report files; write today's report
  next to them.
- If the upstream fetch fails, stop and surface the error — do not fall
  back to a stale local ref.
