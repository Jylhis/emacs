# daviderestivo/homebrew-emacs-head

Homebrew tap with formulae for `emacs-head@26..32`.  Polled by the
`upstream-commit-review` skill (source: `homebrew-emacs-head`).

## Repository

- https://github.com/daviderestivo/homebrew-emacs-head
- Branch: `master`
- Glob: `patches/*.patch` (flat directory, version-suffixed file names
  like `0005-System-appearance-30.patch`, `0014-Skip_ns_color_initialization_in_batch_mode.patch`)

## Patch model

Numbered patch series, applied selectively by each `emacs-head@NN`
formula.  Some patches have multiple version variants (`-26`, `-29`,
`-30`); the active emacs-head@31 formula tends to use the
cross-version (unsuffixed) variant where available.

## Why we track this

Substantial overlap with `homebrew-emacs-plus` (System-appearance is
in both), but `homebrew-emacs-head` carries several NS-specific
patches with no emacs-plus equivalent:

- `0014-Skip_ns_color_initialization_in_batch_mode.patch` — different
  fix shape for the same NS-batch-mode color-list crash that
  emacs-plus addresses with `fix-ns-x-colors.patch`.  Worth a
  side-by-side comparison before absorbing either.
- `0002-Patch-multicolor-font.patch` — fixes color-emoji rendering in
  NS by relaxing macfont's color-glyph rejection.
- `0008-Fix-window-role.patch` — sets `kCGWindowOwnerName` so window
  enumerators and dock badges work correctly.
- `0012-BLOCK_ALIGN.patch` — alignment fix for the experimental
  `unexec` PMAX dump (pre-pdumper era; check whether still relevant
  on this Meson/pdumper-only branch before triaging).

## Verdict expectations

Mixed.  Default verdict for new rows: `unreviewed` — most entries
deserve real triage because the repo doesn't follow the "upstream
everything" policy of emacs-plus.  Expect ~50% to land on
`verify-then-absorb` and the rest on `defer` or `not-applicable`.

## Tracked patches

Run `python3 .claude/skills/upstream-commit-review/scripts/patch_sources.py update-baseline`
after editing per-patch verdicts in
`scripts/state/patch-sources.json`.

## Related fork notes

- [[fork-homebrew-emacs-plus]] — d12frosted's tap, also macOS-focused;
  smaller patch set, "upstream-everything" policy.
- [[fork-macports]] — MacPorts NS-port and Mac-port patches.
