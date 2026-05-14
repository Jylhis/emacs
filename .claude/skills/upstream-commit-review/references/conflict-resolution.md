# Conflict-resolution policy

When `apply.sh` runs `git cherry-pick -x` on an AUTO-bucket commit, the
result is one of:

1. **Clean apply** — committed; bucket unchanged.
2. **Mergiraf-resolved** — a per-file merge driver
   (see `attributes/gitattributes`) produced a conflict-free result on
   C/C++ files; committed; bucket suffix `+mergiraf`.
3. **`-X theirs` retry-resolved** — the conflict matched one of the
   recognized drift patterns below; committed; bucket suffix `+theirs`.
4. **REVIEW** — committed only after manual inspection; bucket
   `conflict:<paths>`.

## Why "prefer upstream" is the default for retries

This fork keeps a small set of intentional divergences (Meson build,
NS bundle layout, `etc/NEWS.31` rename).  Cherry-picked upstream
commits sometimes touch a region that we have *also* edited locally
for an unrelated reason — typically because we adapted code in
`src/keyboard.c`, `src/xdisp.c`, or similar files.

In those cases the upstream change is the *latest* and *most
correct* version of the fix; our local edit was either a temporary
workaround that got obsoleted or an adaptation that needs to be
re-derived on top of the new upstream content.  Taking upstream
("theirs" in the cherry-pick frame of reference) and re-applying our
fork delta on top is therefore safer than the reverse.

When this rule does not apply — for example, when the conflict is in
a file we deliberately rewrote (`src/emacs.c` for the NS bundle, or
the meson build descriptions) — `-X theirs` would clobber that
rewrite.  The retry allowlist below is the safety net.

## Retry tiers (codified)

`apply.sh` walks these in order on a conflict:

### Tier 1 — Clean cherry-pick

`git cherry-pick -x <SHA>`.  If a `.c` / `.h` conflict arises, the
`mergiraf` merge driver registered by `lib.sh` runs first; if it
resolves the file, the commit lands as `+mergiraf`.

### Tier 2 — NEWS.31 redirect

When the only conflicted file is `etc/NEWS.31` AND the upstream
commit's pre-conflict diff touched only `etc/NEWS`, retry with
`-X theirs`.  Git's rename detection has already mapped the upstream
hunk onto `etc/NEWS.31`; the "prefer upstream" rule says: take it.
Bucket suffix `+theirs`; the report's `## Range-diffs of -X theirs
resolutions` section shows what was taken so a human can verify the
NEWS section ordering.

### Tier 3 — Bounded `-X theirs` retry

When the conflict files are a subset of the **drift allowlist**:

- `src/keyboard.c`
- `src/xdisp.c`
- `src/coding.c`
- `etc/AUTHORS`

retry with `-X theirs`.  These files routinely drift between our
fork and upstream and the "prefer upstream" rule applies.  The
allowlist is configurable via `apply.sh --retry-allow=PATH,...`.

Bucket suffix `+theirs`.  A range-diff is recorded in the report.

### Tier 4 — Abort and demote

Any other conflict aborts the cherry-pick and demotes the commit to
the REVIEW pile with reason `conflict:<paths>`.

The user's options at that point are:

1. Resolve by hand and commit.  `git rerere` (already enabled
   repo-wide) records the resolution; future runs that hit the same
   conflict shape auto-resolve.
2. Run `git imerge start` to break the offending merge into
   bisectable pairwise micro-merges, useful for cascading conflict
   chains (e.g. the GTK3 child-frame series).
3. Skip the commit entirely if the upstream change does not apply to
   this fork's scope.

## When `-X theirs` is wrong

Do *not* extend the drift allowlist to:

- `src/emacs.c` — heavily adapted for the NS bundle's
  `ns_self_contained` layout.
- `meson.build` / `src/meson.build` / any `meson*` file — our own
  build description; upstream still uses autotools.
- `nextstep/` — fork-specific NS bundle assembly.
- `etc/NEWS.31` content unrelated to upstream's `etc/NEWS` (i.e.
  pure local edits that have no upstream counterpart).

If a conflict in any of those files turns up, abort and triage
manually.  This is what tier 4 is for.

## Recording deviations

When the user manually resolves a tier-4 REVIEW commit and the
resolution differs from the "prefer upstream" rule, note it in the
commit message body:

```
; Backport: <upstream subject>

Local divergence kept: <one-line reason>.
* path/to/file (function): describe the conflict.
```

The leading `; ` keeps the commit out of the generated ChangeLog
(per CONTRIBUTE) but the `Backport:` keyword is recognized by
`admin/gitmerge.el` for future merge filtering.
