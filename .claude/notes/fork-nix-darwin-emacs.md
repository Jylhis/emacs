# nix-giant/nix-darwin-emacs

Nix overlay providing bleeding-edge Emacs builds for macOS (Darwin).
Forked from nix-community/emacs-overlay, focuses solely on the Emacs
binary (not MELPA/ELPA packages).

## Repository

- https://github.com/nix-giant/nix-darwin-emacs
- 29 stars, MIT license
- Actively maintained, daily CI updates (last commit 2026-04-27)

## Structure

Nix flake exposing `emacs-29`, `emacs-30`, `emacs-unstable` via an
overlay (`overlays.emacs`).  Pins exact commits from emacs-mirror/emacs,
auto-updated daily.

## Patches Applied

All patches originate from **homebrew-emacs-plus** (d12frosted).

### 1. system-appearance.patch (by Nicolas G. Querol)

**NOT upstreamed.**  Files: `src/frame.h`, `src/nsfns.m`, `src/nsterm.m`

Adds:
- `ns-system-appearance` variable (reports `dark` or `light`)
- `ns-system-appearance-change-functions` hook
- KVO on `effectiveAppearance` for real-time detection
- Uses `NSAppearanceNameDarkAqua` (correct API since Mojave 10.14)

Enables automatic theme switching:
```elisp
(add-hook 'ns-system-appearance-change-functions
          (lambda (appearance)
            (pcase appearance
              ('light (load-theme 'tango t))
              ('dark (load-theme 'tango-dark t)))))
```

### 2. round-undecorated-frame.patch (by Boris Buliga)

**NOT upstreamed.**  Files: `src/frame.c`, `src/frame.h`, `src/nsfns.m`,
`src/nsterm.h`, `src/nsterm.m`

Adds `undecorated-round` frame parameter -- creates frames without
title bar but with macOS-native rounded corners.  Uses
`NSFullSizeContentViewWindowMask`, transparent titlebar, hidden
window buttons.  Adds `FRAME_UNDECORATED_ROUND` macro and
`ns_set_undecorated_round`.

### 3. fix-window-role.patch (by Boris Buliga)

**Already upstreamed** into Emacs master.  Only applied to 29/30.
One-line fix: accessibility role from `NSAccessibilityTextFieldRole`
to `NSAccessibilityWindowRole`.

### 4. adjust-ns-init-colors.patch (unstable only)

**NOT upstreamed.**  File: `src/emacs.c`

Moves `ns_init_colors()` call to after `init_callproc()` (which sets
`data-directory`).  Fixes startup color initialization failure.

## Other Build Modifications

- Custom 3D Emacs.icns icon (Valeriy Savchenko)
- EmacsClient.app macOS bundle (wraps `emacsclient --create-frame`)
- Git revision injection into `lisp/loadup.el`
- Darwin-only platform restriction

## Absorb verdict (downstream — into `jylhis/emacs`)

This overlay just **re-hosts** patches whose source of truth is
[homebrew-emacs-plus](fork-homebrew-emacs-plus.md).  When deciding
what to absorb into `jylhis/emacs`, the homebrew-emacs-plus note is
authoritative — the rows below mirror its verdicts, with cross-
references.

| Patch | Verdict | Reason |
|---|---|---|
| `patches-31/system-appearance.patch` | **absorb-now** | See [emacs-plus row](fork-homebrew-emacs-plus.md#system-appearancepatch--absorb-now) |
| `patches-31/round-undecorated-frame.patch` | **absorb-now** | See [emacs-plus row](fork-homebrew-emacs-plus.md#round-undecorated-framepatch--absorb-now) |
| `patches-unstable/adjust-ns-init-colors.patch` | **not-applicable** | Already in this fork — bug#80377 (`b7aca342e69`) + bug#80752 (`112a2c4595d`).  Confirm with `grep -n "ns_init_colors" src/emacs.c` (L2077). |
| `patches-30/fix-window-role.patch` | **not-applicable** | Already upstream as bug#77062 (`6e1054a40bf`). |

This overlay does **not** ship `fix-ns-x-colors.patch`, which
homebrew-emacs-plus does carry — see the emacs-plus note for that
candidate.

## Polling

The patch-source poll in `.claude/skills/upstream-commit-review`
tracks this overlay under the name `nix-darwin-emacs` with glob
`overlays/patches-31/*.patch`.  When emacs-31 reaches EOL, bump the
glob to `overlays/patches-32/*.patch`.

## Reference value

Still useful as a downstream-consumer canary even after the per-patch
verdicts are resolved: it builds the Darwin patches against master
daily, so if upstream master breaks them, this overlay's CI catches
it first.
