# Homebrew emacs-plus (d12frosted)

Homebrew tap that ships Darwin-focused builds of Emacs with a curated
set of patches.  This is the **origin** of the Darwin patches that
nix-giant/nix-darwin-emacs (and from there, jotain's `emacs.nix`)
re-host into the Nix overlay; tracking emacs-plus directly catches new
patches before they propagate downstream.

## Repository

- https://github.com/d12frosted/homebrew-emacs-plus
- Maintainer: Boris Buliga (@d12frosted) + community
- 3.6k stars, GPL/MIT mixed (formulae GPL-compatible)
- Patches live at `patches/emacs-NN/*.patch`, one directory per Emacs
  major version.

## Patches tracked (as of 2026-05-20)

### `patches/emacs-31/`

| File | Author | Touches | Verdict for `jylhis/emacs` |
|---|---|---|---|
| `system-appearance.patch` | Nicolas G. Querol (2020) | `src/frame.h`, `src/nsfns.m`, `src/nsterm.m` | **absorb-now** |
| `round-undecorated-frame.patch` | Boris Buliga (2024) | `src/frame.c`, `src/frame.h`, `src/nsfns.m`, `src/nsterm.h`, `src/nsterm.m` | **absorb-now** |
| `fix-ns-x-colors.patch` | (emacs-plus) | `lisp/term/ns-win.el` | **verify-then-absorb** |

### `patches/emacs-30/` (reference only — 30-line)

| File | Touches | Verdict for `jylhis/emacs` |
|---|---|---|
| `system-appearance.patch` | same as 31 | tracked in the 31 row above |
| `round-undecorated-frame.patch` | same as 31 | tracked in the 31 row above |
| `fix-ns-x-colors.patch` | same as 31 | tracked in the 31 row above |
| `fix-macos-tahoe-scrolling.patch` | macOS 26 scrolling-lag fix | **not-applicable** — already upstream as bug#80268 (`1c4f09aadc4`, `046f5ef0189`) |
| `fix-window-role.patch` | `NSAccessibility` role | **not-applicable** — already upstream as bug#77062 (`6e1054a40bf`) |
| `treesit-compatibility.patch` | renames `:eq?`/`:match?`/`:pred?` back to the older spellings for tree-sitter 0.26 | **not-applicable** — this fork already uses the new predicate names in `doc/lispref/parsing.texi` |

## Verdict detail

### `system-appearance.patch` — absorb-now

Adds an `ns-system-appearance` variable + `ns-system-appearance-change-functions`
hook driven by KVO on `[NSApp effectiveAppearance]`.  Uses
`NSAppearanceNameDarkAqua` (correct since Mojave 10.14, replaces the
deprecated `NSAppearanceNameVibrantDark`).

Confirmed missing from this fork:

    $ grep -rn "ns-system-appearance\|systemDidChangeAppearance" src/
    (no matches)

Most-requested macOS feature for upstream Emacs; landing it in
`jylhis/emacs` lets `jotain/`'s `init.el` switch themes on system
appearance change without an external shell-out.  The patch is clean,
well-scoped, and unchanged across emacs-29 → emacs-31 dirs.

### `round-undecorated-frame.patch` — absorb-now

Adds the `undecorated-round` frame parameter — renders frames with no
title bar but with macOS-native rounded corners via
`NSFullSizeContentViewWindowMask` + transparent titlebar + hidden
window buttons.  Adds `FRAME_UNDECORATED_ROUND` macro and
`ns_set_undecorated_round`.

Confirmed missing from this fork:

    $ grep -rn "Qundecorated_round\|undecorated-round" src/
    (no matches)

Niche, but the implementation is self-contained and the rest of the
overlay (nix-darwin-emacs / nix-emacs-overlay) already builds against
it on every CI cycle, so it's well-exercised.

### `fix-ns-x-colors.patch` — verify-then-absorb

Refreshes `x-colors` during NS `window-system-initialization` so that
dumps built in a headless environment (where `ns-list-colors` returns
~62 colors) don't permanently see a truncated palette at runtime
(where ~800+ colors are available).

Confirmed missing from this fork:

    $ grep -n "x-colors\b\|ns-list-colors\b" lisp/term/ns-win.el
    (no matches; only window-system-initialization at L807 + x-apply-session-resources at L872)

Confirmed missing from `emacs-upstream/master`:

    $ git log emacs-upstream/master --grep="x-colors\|ns-list-colors" -i --since=2022-01-01
    (only Haiku and PGTK changes; no NS x-colors refresh)

Discovered during the 2026-05-20 survey; not in nix-darwin-emacs's
`patches-31/` dir, so the existing
[fork-nix-darwin-emacs.md](fork-nix-darwin-emacs.md) note misses it.

Verify before absorbing whether this fork dumps Emacs in a headless
environment (Nix's sandbox + Meson `bootstrap-emacs`).  If yes, the
patch is necessary; if the dump already runs against a real display
the bug is masked.

## Build modifications (not patches; reference only)

emacs-plus also customizes the macOS app bundle (custom 3D `Emacs.icns`,
`EmacsClient.app` wrapper, GnuTLS auto-renewal, plist tweaks).  These
ship from the formula, not the patch tree, and are out of scope for
absorption into the source.

## Polling

Tracked by `.claude/skills/upstream-commit-review`'s patch-source poll
step (`attributes/patch-sources.toml`, name `homebrew-emacs-plus`,
glob `patches/emacs-31/*.patch`).  The skill compares SHA-256 of each
patch body against the baseline in
`scripts/state/patch-sources.json`; new or changed patches surface in
the next report under "Patch-source drift" with a placeholder verdict
row.

When the 31 cycle ends, bump the glob to `patches/emacs-32/*.patch`
(or whichever directory emacs-plus adds for the next cycle).
