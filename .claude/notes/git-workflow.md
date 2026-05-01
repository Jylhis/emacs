# Git Workflow Notes

Sources: admin/notes/git-workflow, admin/notes/repo, CONTRIBUTE.

## Branching model

- **master**: Active development.
- **emacs-NN**: Release branches (e.g., emacs-30).  More conservative,
  bug fixes and doc fixes only.
- **feature/***: Long-lived feature branches.  Merged (not
  cherry-picked) to master.  No force pushes.  CI runs on EMBA.
- **scratch/***: Throw-away branches.  Force pushes tolerated.  Not
  merged; commits may be poor quality.

## Recommended setup (admin/notes/git-workflow)

    git config --global transfer.fsckObjects true
    git config push.default current

Use worktrees for parallel branch access:

    git worktree add ../emacs-30 emacs-30

## Bug fixes go to the release branch

Install bug fixes on the release branch only; let gitmerge sync them
to master.  Do NOT manually cherry-pick to both branches -- it makes
merges harder.

Exception: if the fix will be hard to merge (divergent code), apply to
both and mark the release-branch commit with "Not to be merged to
master" (or "Backport:" prefix).

## Documentation fixes

Always safe for the release branch, even during feature freeze.
Limited to fixing real problems -- no cleanups or stylistic changes.

## Merging release -> master

Use `admin/gitmerge.el`:

    emacs -l admin/gitmerge.el -f gitmerge

- Defaults to merging `origin/emacs-30`.
- Shows commits not yet merged.  Mark with 's' to skip.
- Handles "Backport:" and "do not merge" automatically.
- Resolves some conflicts automatically.

## Feature branches (admin/notes/repo)

- Avoid merging from master during development.  Merge once at the
  end.
- Single-commit branches: merge directly.
- Few real commits + many "merge from master": take the diff and apply
  as a single commit instead.

## Bisecting (admin/notes/repo)

Use the smart bisect starter:

    ./admin/git-bisect-start [good] [bad]

Skips external-tree merges and known-broken commits.

## Reverting on release branch

If a release-branch commit should only be on master: revert it on the
release branch with "do not merge to master" in the log.  This
prevents the revert from propagating to master via gitmerge.

## Commit conventions (summary)

- Present tense.
- 50-char summary, no trailing period.
- ChangeLog entries: max 78 chars (63 preferred).
- Reference bugs as (Bug#NNNNN).
- No Signed-off-by lines.
- Only printable UTF-8.
- Prefer https: URLs.
- See .claude/rules/commits.md for full rules.
