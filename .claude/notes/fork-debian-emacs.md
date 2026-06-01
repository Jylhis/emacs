# Debian — emacsen-team/emacs

Debian's GNU Emacs source package.

**Not currently polled** by the `upstream-commit-review` skill:
salsa.debian.org's smart-http endpoint returns 401 for anonymous
clones even of public repos, so the poll step's
`git clone --depth 1` fails.  If we want to track this source, we'd
need to either (a) ship a Salsa token in the harness, (b) switch the
poll step to the GitLab raw-blob API, or (c) maintain a local mirror.
None of these is worth the effort right now — the patch set is
~60% Debian-specific branding and test triage; only a handful of
entries (e.g. the occasional already-upstreamed fix duplicated here)
would be actionable.  Check this source manually when investigating
a known Debian Bug# in upstream Emacs.

## Repository

- https://salsa.debian.org/emacsen-team/emacs.git
- Branch: `master`
- Glob: `debian/patches/*.patch` (numbered patch series, quilt-style)

## Patch model

Numbered debian patch series (`0001-…` through `00NN-…`), applied by
`debian/rules` via `quilt push` before the upstream build runs.  Most
entries are Debian distribution policy: branding (Debian flavor,
paths, info-pages), test triage (many `Mark-*-as-unstable` entries to
keep the build green on Debian's autobuilders), native-comp tuning
(`async-jobs-number=1`, conservative defaults for shared-server
builds), and the occasional real upstream bug fix.

## Why we track this

Mostly noise from the fork's perspective, but the occasional bug fix
lands here before upstream merges it (Debian routinely cherry-picks
upstream HEAD).  Per-patch verdicts will filter out the obvious
distro-specific entries.

## Verdict expectations

Default verdict for new rows: `unreviewed`.  Expected breakdown:

- ~60% `not-applicable` — Debian branding, paths, test triage,
  conservative native-comp defaults.
- ~30% `defer` — Build fixes for architectures this fork doesn't
  target (m68k DUMP_RELOC, distro-specific PURESIZE bumps).
- ~10% real fixes worth `verify-then-absorb` — typically duplicates
  of upstream fixes that have already landed.

## Tracked patches (as of 2026-05-31)

Sampled 26 numbered patches.  Notable entries:

| Patch (prefix) | Likely verdict | Note |
|---|---|---|
| `0001-Update-debian-version.patch` | `not-applicable` | Debian branding. |
| `0002-Add-Debian-flavor.patch` | `not-applicable` | Branding. |
| `0022-Add-public-interfaces-for-accessing-builtin-package-` | `verify-then-absorb` | Generic upstream-worthy change; check whether already in this fork. |
| `0025-src-image.c-svg_load_image-Fix-off-by-one-mistake-bug-80851` | `not-applicable` | Bug#80851 — absorbed upstream; Debian has not removed yet. |
| `Mark-*-as-unstable.patch` (multiple) | `not-applicable` | Debian autobuilder test triage. |

Run `python3 .claude/skills/upstream-commit-review/scripts/patch_sources.py update-baseline`
after editing per-patch verdicts.

## Related fork notes

(no closely related fork notes; this is the only non-Mac patch source
currently tracked.)
