---
name: upstream-commit-review
description: Fetch new commits from GNU Emacs upstream (savannah) and triage them for backport into this fork. Auto-cherry-picks safe categories (docs, lisp bug fixes with Bug#NNNNN, lisp docstring/style fixes, test-only changes, small src/ fixes, lisp+NEWS Bug# fixes with NEWS-port note) and writes a markdown report of the rest under .claude/notes/. Use when the user asks to sync upstream, review upstream commits, or backport upstream changes.
---

# Upstream commit review

Triage commits from GNU Emacs upstream (`git.savannah.gnu.org`) for
backport into this fork.  This fork has diverged from upstream in ways
that make a plain `git merge upstream/master` painful — most notably,
the autotools entry points (`configure.ac`, `autogen.sh`, `make-dist`,
all `Makefile.in`, `GNUmakefile`) were removed at commit `313f867`,
and `etc/NEWS` was renamed to `etc/NEWS.31`; the build is now
Meson-only.  This skill applies safe upstream changes automatically
and writes a markdown report listing what needs human review.

## Pre-flight (always run first)

1. The working tree must have no *user* changes and HEAD must not be
   detached.  Untracked files under `.claude/`, `.direnv/`, `build*/`,
   or `node_modules/` are harness/build state and are ignored:

   ```bash
   git status --porcelain \
     | grep -Ev '^\?\? (\.claude/|\.direnv/|build[^/]*/|node_modules/)' \
     | head
   git symbolic-ref -q HEAD
   ```
   If the filtered status output is non-empty or the symbolic-ref
   check fails, stop and tell the user.

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
   git fetch emacs-upstream master || {
       echo "fetch from emacs-upstream failed; refusing to use stale ref" >&2
       exit 1
   }
   ```

## Determine the commit range

Use `git merge-base` to find the most recent common ancestor between
this branch and upstream — that is the sync point regardless of how
previous merges were spelled.

```bash
ANCHOR=$(git merge-base HEAD emacs-upstream/master)
ANCHOR_DATE=$(git show -s --format=%ci "$ANCHOR")
BEHIND=$(git rev-list --count "$ANCHOR"..emacs-upstream/master)
```

List the commits to triage.  `--cherry-pick --right-only` skips
upstream commits whose **patch-id** is already in our history —
typical for a long-lived fork where some changes have been backported
under a different SHA.  `--no-merges` excludes upstream's own merge
commits.

```bash
git log --reverse --no-merges --cherry-pick --right-only \
        --format='%H' HEAD...emacs-upstream/master
```

**Patch-id miss case**: a commit can leak through if it was a pure
file-content move/rename upstream but became a content edit locally
(e.g. `etc/NEWS` rename + later in-file edits change the patch-id).
Augment the skip set by parsing `(cherry picked from commit ...)`
trailers from our local history since `ANCHOR`:

```bash
git log --format='%B' "$ANCHOR"..HEAD \
  | sed -n 's/.*cherry picked from commit \([0-9a-f]\{40\}\).*/\1/p' \
  | sort -u > /tmp/already-cherry-picked
```

Filter that out of the candidate list before classifying; record the
count separately as "Trailer-deduped" in the report.

If the resulting list is empty:

- when `BEHIND == 0`: write a one-line "no new upstream commits"
  report and stop.
- otherwise: write an "all candidates already cherry-picked" report
  noting both the cherry-pick filter count and the trailer-set count.

## Per-commit classification

For each candidate `SHA`, gather metadata once:

```bash
SUBJECT=$(git show -s --format=%s "$SHA")
FILES=$(git show --name-only --format= "$SHA" | sed '/^$/d')
LINES=$(git show --shortstat --format= "$SHA" \
        | awk '/files? changed/ {
                 for (i=1; i<=NF; i++)
                   if ($i ~ /^[0-9]+$/ && $(i+1) ~ /(insertion|deletion)/) s += $i
               } END { print s+0 }')
MISSING=$(while IFS= read -r f; do [ -e "$f" ] || echo "$f"; done <<<"$FILES")
```

Apply the rules **in order**, first match wins:

| # | Bucket | Match | Action |
|---|---|---|---|
| 1 | SKIP / autotools | any file matches `^(configure\.ac\|autogen\.sh\|make-dist\|GNUmakefile)$`, `Makefile\.in$`, or `^m4/` | report only |
| 2 | SKIP / merge-noise | subject matches `^Merge ` or contains `gitmerge` (also catches subjects like `; Merge from origin/emacs-31`).  A leading `; ` only means "do not generate a ChangeLog entry" per CONTRIBUTE — those are real changes (typo fixes, docstring fixes, NEWS edits) and must fall through to the file-based rules below. | report only |
| 3 | SKIP / admin churn | every file is under `admin/` or matches `^ChangeLog(\.[0-9]+)?$` | report only |
| 4 | AUTO / doc-only | every file matches `^doc/`, `^etc/(NEWS(\.[0-9]+)?\|ERC-NEWS\|HISTORY\|AUTHORS)$`, `\.texi(nfo)?$`, or `\.org$` | cherry-pick |
| 5 | AUTO / test-only | every file matches `^test/` | cherry-pick |
| 6 | AUTO / lisp bugfix | subject contains `Bug#` AND every file matches `^lisp/` or `^test/` | cherry-pick |
| 7 | AUTO / lisp doc-or-style fix | every file matches `^lisp/.+\.el$`, `LINES < 50`, AND (subject begins with `; ` OR subject matches case-insensitive `\b(docstring\|doc string\|doc fix\|typo\|when-let\|comment fix)\b`) | cherry-pick |
| 8 | AUTO / small src fix | every file matches `^src/`, `LINES < 50`, AND any of: subject begins with `Fix `, `; Fix `, `Pacify `, `Avoid `, `; Avoid `, `Don't `, or `; * src/`; OR subject contains `Bug#`; OR `LINES < 20` | cherry-pick |
| 9 | AUTO / lisp+NEWS Bug# | subject contains `Bug#` AND every file matches `^lisp/`, `^test/`, or `^etc/NEWS(\.[0-9]+)?$` | cherry-pick (NEWS hunk redirected, see below) |
| 10 | REVIEW | everything else | report only |

A commit with non-empty `MISSING` is **forced** to REVIEW with reason
`missing-file:<first missing path>`, regardless of bucket — taking it
verbatim would create dangling references (e.g. an upstream commit
that touches `lisp/textmodes/markdown-ts-mode-x.el`, which doesn't
yet exist in this fork).

### Why-column conventions for REVIEW rows

Replace the legacy `unclassified` reason with a short tag explaining
which rule was almost matched, so the human can triage faster:

| Tag | Meaning |
|---|---|
| `lisp-multi-area` | lisp/ + something else (etc/NEWS, doc/, src/) |
| `lisp-no-bug` | lisp-only but no `Bug#` and not docstring-shaped |
| `src-multi-file` | src/ touching > 1 file or > 50 lines |
| `feature` | new user-visible command/option |
| `large` | LINES ≥ 200 |
| `conflict:<paths>` | cherry-pick aborted; record the conflicted paths |
| `missing-file:<path>` | references a file not in HEAD |
| `news-port-required` | applied; NEWS hunk needs porting to NEWS.31 |

## Cherry-pick (AUTO buckets only)

```bash
if git cherry-pick -x "$SHA"; then
    NEW_SHA=$(git rev-parse HEAD)
    # record APPLIED row: SHA, NEW_SHA, SUBJECT, bucket
elif news_only_conflict; then
    : # handled inside news_only_conflict (see next section)
else
    # Capture conflicted paths before aborting.
    CONFLICTED=$(git diff --name-only --diff-filter=U | tr '\n' ',' | sed 's/,$//')
    if ! git cherry-pick --abort 2>/dev/null; then
        echo "cherry-pick --abort failed for $SHA — manual cleanup required" >&2
        exit 1
    fi
    # demote to REVIEW with reason "conflict:$CONFLICTED"
fi
```

`-x` records the original SHA in the commit message so future
`gitmerge` runs and the trailer-set patch-id dedupe (above) detect
that the change is already present.

### etc/NEWS redirect (rule 9 / NEWS-only conflicts)

This fork moved `etc/NEWS` → `etc/NEWS.31`.  Upstream commits that
modify `etc/NEWS` will conflict deterministically; treat that
specifically:

```bash
news_only_conflict() {
    local conflicted
    conflicted=$(git diff --name-only --diff-filter=U)
    [ "$conflicted" = "etc/NEWS" ] || return 1
    [ ! -e etc/NEWS ] || return 1
    # The file is "modified by them, deleted by us" — choose --ours
    # (the deletion), continue the cherry-pick, and record a note
    # asking the human to port the upstream NEWS hunk to NEWS.31.
    git rm -f etc/NEWS
    GIT_EDITOR=true git cherry-pick --continue || return 1
    echo "$SHA" >> /tmp/news-port-required
    return 0
}
```

Mark these rows in the APPLIED table with bucket suffix
`+news-port-required`.  Render the dropped NEWS hunk(s) verbatim under
a dedicated section of the report so the user can copy them into
`etc/NEWS.31`.

### Conflict resolution policy

Outside of the NEWS redirect above, **never resolve conflicts
automatically** — abort and demote to REVIEW.  When the user later
resolves a REVIEW commit by hand, the convention for this fork is:

> When our local edits overlap an upstream fix that does the same
> thing, prefer upstream.

Record any deviation from that rule in the commit message of the
backport so future audits can see why.

## Report

Write to:

```
.claude/notes/upstream-backport-review-$(date -u +%Y-%m-%dT%H%M).md
```

and update `.claude/notes/upstream-backport-review-latest.md` to
point at it (symlink, or rewrite the file with a one-line redirect if
symlinks are unavailable on this filesystem).  Multiple runs in a
single day must not destroy each other's reports.

Structure:

```markdown
# Upstream backport review — <YYYY-MM-DDTHHMM UTC>

- Anchor commit: `<SHA>` (<subject>) — <ANCHOR_DATE>
- Range: `<ANCHOR>..emacs-upstream/master` (<BEHIND> commits behind)
- Reviewed: <N>   Applied: <A>   Needs review: <R>   Skipped: <S>
- Trailer-deduped: <T>
- News-port-required: <P>

## Applied

| Original SHA | New SHA | Subject | Bucket |
|---|---|---|---|
| ... | ... | ... | doc-only / test-only / lisp-bugfix / lisp-doc-style / small-src / lisp+news-bug+news-port-required |

## Needs review (grouped by area)

### src/
| SHA | Subject | Lines | Why |
|---|---|---|---|
| ... |

### lisp/treesit
| ... |

### lisp/vc/
...

## Skipped

| SHA | Subject | Reason |
|---|---|---|
| ... | ... | autotools / merge-noise / admin |

## NEWS hunks needing port to etc/NEWS.31

For each commit tagged `news-port-required`, include the dropped
upstream NEWS hunk verbatim under `### <SHA> — <subject>` so the user
can copy lines into `etc/NEWS.31` in a follow-up commit.
```

Group `Needs review` rows by area, where the area is the longest
common path prefix collapsed to a directory: `src/`,
`lisp/treesit`, `lisp/vc/`, `lisp/erc/`, `lisp/textmodes/sgml-mode`,
`lisp/emacs-lisp/`, etc.  Group order: `src/`, `lisp/`, `doc/`,
`etc/`, `lib-src/`, `test/`, other.

Truncate the `Files`/`Why` columns to fit one line; keep each table
row on one physical line so the report stays grep-able.

If no candidates remain after dedupe:

```markdown
# Upstream backport review — <YYYY-MM-DDTHHMM UTC>

No upstream commits to triage. Anchor `<SHA>` (<date>); 0 behind.
```

If candidates were all classified as REVIEW:

```markdown
- Note: no commits matched any AUTO bucket this run.
```

## Final user message

After writing the report, print:

1. The summary counts: Reviewed / Applied / Needs review / Skipped /
   Trailer-deduped / News-port-required.
2. The relative path to the report file (and the latest pointer).
3. The number of new commits now on `$BRANCH`
   (`git rev-list --count "$ANCHOR"..HEAD`).
4. If any NEWS-port-required entries: a one-liner pointing the user
   at the report's NEWS-port section.
5. **Reminder**: nothing has been pushed.  Recommend the user run
   `meson test -C build --suite smoke` before pushing, and inspect
   each cherry-picked commit (`git log --oneline "$ANCHOR"..HEAD`).
6. Point at `.claude/rules/commits.md` and
   `.claude/notes/git-workflow.md` for backport conventions if the
   user plans to merge to `dev`.

## Guard rails

- Never push, never switch branches, never `git reset --hard`.
- Outside of the explicit `etc/NEWS` redirect, never resolve
  conflicts; always abort and demote to REVIEW.  If
  `cherry-pick --abort` itself fails, hard-stop with an error
  describing what to fix — do not leave the index in a half-resolved
  state.
- Never delete previously generated report files; write today's
  report next to them with a unique timestamp.
- If the upstream fetch fails, stop and surface the error — do not
  fall back to a stale local ref.

## Known footguns

- `Makefile\.in$` in rule 1's regex would also match
  `lisp/Makefile.in` if such a path existed.  None do on this branch
  after the autotools removal, but be aware if this skill is reused
  on another fork.
- `--cherry-pick --right-only` filters by `git patch-id`, which
  normalizes whitespace but not diff context.  A commit whose context
  shifted upstream relative to our local copy can dedupe; one whose
  *content* changed even slightly cannot.  The trailer-set augment
  above catches the second case for our own cherry-picks.
- Rules 4–9 are mutually exclusive given "first match wins", but the
  edge case `lisp/ + doc/ + Bug#` falls through to REVIEW today.
  Promote it to AUTO if the human-review burden warrants it; rule 9
  already covers `lisp/ + etc/NEWS + Bug#`.
- The fork is NS-focused.  X11/GTK3 changes apply cleanly on the
  source side but exercise code paths we don't routinely build, so
  even when they land in AUTO buckets, smoke-test before pushing.
