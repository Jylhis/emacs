# jimeh/build-emacs-for-macos

CI repository that ships pre-built macOS Emacs.app bundles for every
master commit.  Polled by the `upstream-commit-review` skill (source:
`jimeh-build-emacs-for-macos`).

## Repository

- https://github.com/jimeh/build-emacs-for-macos
- Branch: `main`
- Glob: `patches/emacs-*/*.patch` (per-version subdirs)

## Patch model

Minimal — the repo's stated policy is to upstream every patch quickly.
Current contents (2026-05-31):

```
patches/emacs-29/ns-alpha-background.patch
```

The repo previously carried more patches; most have been merged upstream.

## Verdict expectations

Default verdict for new rows: `verify-then-absorb` — small surface,
real NS code, but check upstream Bug# status before applying because
patches here tend to land in GNU Emacs shortly after appearing here.

## Tracked patches (as of 2026-05-31)

| Patch | Verdict | Note |
|---|---|---|
| `emacs-29/ns-alpha-background.patch` | `verify-then-absorb` | Bug#65198 — plumbs `alpha-background` frame parameter through NS (`src/nsfns.m`, `src/nsterm.m`, `src/macfont.m`).  Check `grep -r alpha_background src/ns*.m src/macfont.m` before absorbing — if already in this fork, mark `not-applicable`. |

## Related fork notes

- [[fork-homebrew-emacs-plus]] — d12frosted's tap; comparable per-patch
  policy for the same NS audience.
- [[fork-homebrew-emacs-head]] — daviderestivo's tap; broader patch set.
