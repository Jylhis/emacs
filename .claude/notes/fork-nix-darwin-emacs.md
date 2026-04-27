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

## Cherry-Pick Feasibility

**Three patches are directly applicable** to this GNU Emacs tree:

1. **system-appearance.patch** -- High value.  Touches nsterm.m,
   nsfns.m, frame.h.  Clean, well-scoped.  Most requested macOS
   feature for upstream Emacs.  Could be submitted as a bug report.

2. **round-undecorated-frame.patch** -- Medium value.  Niche but
   clean implementation.  Touches frame.c/h, nsfns.m, nsterm.m/h.

3. **adjust-ns-init-colors.patch** -- Small fix to src/emacs.c.
   Worth verifying if the bug exists on master.

The fix-window-role patch is already in master.
