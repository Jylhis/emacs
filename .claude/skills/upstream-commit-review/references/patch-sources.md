# Patch-source poll — design

The upstream-commit-review skill's primary job is to cherry-pick
commits from `git.savannah.gnu.org/git/emacs.git`.  Several Darwin /
packaging-focused repos that `jotain/`'s Nix build references (or
that we want to track for completeness) ship their changes as
**`.patch` files in a git tree**, not as commits we can cherry-pick:

- `nix-giant/nix-darwin-emacs` — re-hosts a curated subset of
  `d12frosted/homebrew-emacs-plus` into a Nix overlay.
- `d12frosted/homebrew-emacs-plus` — source of truth for the Darwin
  patch set (system-appearance, round-undecorated-frame, etc.).
- `macports/macports-ports` — Portfile + bundled patches for
  `editors/emacs` and `aqua/emacs-mac-app`.

The poll step in `scripts/patch_sources.py` runs alongside the
cherry-pick loop and adds two new sections to the run's report:
"Patch-source drift" and "Patch-source candidates".

## Why file-based diff, not cherry-pick

These patches are not commits against this fork's history.  They are
diffs (often hand-rewritten from upstream contributors' originals)
that the downstream packagers re-apply to each new release.  Trying
to `git cherry-pick` them against `patches` would either fail outright
(missing parent SHA) or land an unrelated commit.

Instead, the poll fingerprints each patch by SHA-256 of its file
body, compares against a committed baseline, and surfaces:

- **new** — a patch file the source ships that the baseline didn't
  know about.  Default verdict `unreviewed`.
- **changed** — same path, different body.  Keeps the previous human
  verdict so the change is re-reviewed against the prior decision.
- **removed** — baseline had a path the source no longer ships.
  Usually means upstream absorbed it; verify by searching
  `emacs-upstream/master` and then drop the baseline entry.
- **unchanged** — for completeness; only appears in verbose output.

## Why store the baseline in the repo

`scripts/state/patch-sources.json` is committed so that running the
poll on a fresh clone immediately knows the verdict it last reached
for each tracked patch.  Without it, every clone would see every
known patch as `new` and re-prompt for verdicts.

The schema is intentionally tolerant — only `sha256` is required per
entry; `verdict` and `note` are optional and default to `unreviewed`
and `""`.

## Retention policy for clones

Clones live under `${RUN_DIR}/sources/<name>`.  `RUN_DIR` is the
per-invocation `mktemp -d` that `scripts/lib.sh` already establishes
for cherry-pick state; OS temp cleanup reaps it without help.  Set
`RUN_DIR` in the environment to direct clones elsewhere (e.g. for
debugging).  The poll re-clones from scratch on every run; we trade
a few seconds of `git clone --filter=blob:none` for guaranteed
freshness and zero on-disk drift between runs.

## Adding a new source

1. Append a `[[source]]` block to
   `attributes/patch-sources.toml`.
2. Run `python3 scripts/patch_sources.py update-baseline`.
3. Open `scripts/state/patch-sources.json`, fill in the per-patch
   `verdict` and `note` you decided on during manual review.
4. Commit both the manifest and the baseline together.

## Verdict values

Valid `verdict` strings (enforced soft — anything else just renders
verbatim in the report):

| Verdict | Meaning |
|---|---|
| `absorb-now` | Land in `jylhis/emacs` next backport batch. |
| `verify-then-absorb` | Probably wanted; needs a build-flag / regression check first. |
| `defer` | Useful but tied to a downstream-specific concern (path layout, launchd, …). |
| `not-applicable` | Already upstream, or architecturally incompatible. |
| `unreviewed` | Default for `new` rows; replace at the next run. |

## Why some sources are opt-in (commented out)

`aquamacs` is a full-source-diff fork against Emacs 29.4, not a
per-file `.patch` set.  Tracking it with this mechanism would surface
hundreds of `changed` rows whenever its branch advances.  Keep it
manual under `.claude/notes/fork-aquamacs.md` instead.

## Wiring with `apply.sh`

`apply.sh` invokes `patch_sources.py report --report-tsv …` after the
cherry-pick loop unless `--skip-patch-sources` is passed.  The TSV is
read by `report.py`, which appends the drift section to the existing
markdown report.  When the cherry-pick loop is in `--dry-run` mode
the patch-source poll still runs and prints its TSV to stdout for
the operator to inspect.

## Failure mode

If a clone fails (network, deleted repo, renamed branch),
`patch_sources.py` writes a single row of the form
`<name>\t(clone-failed)\terror\tunknown\t<stderr-excerpt>` to the
TSV and continues with the next source.  The cherry-pick batch is
unaffected.
