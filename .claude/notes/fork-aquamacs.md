# Aquamacs Emacs

Modified GNU Emacs distribution for macOS, aiming to be a
"Mac-native" Emacs with standard macOS keybindings, one-buffer-
per-window, and bundled packages.

## Repository

- https://github.com/aquamacs-emacs/aquamacs-emacs
- 423 stars, 41 forks, GPL-3.0
- Created 2005, on GitHub since 2009
- Website: http://aquamacs.org

## Maintainers

- David Reitter (creator, 2005-2019)
- Win Treese (current maintainer, since ~2019)

## Branches and Base Versions

| Branch           | Base Emacs | Status                         |
|------------------|------------|--------------------------------|
| aquamacs3        | 25.3.50    | Stable release (3.6), dormant since 2023 |
| aquamacs-4-dev   | 29.4       | Active development (last: 2026-04-20) |

## Architecture

Full GNU Emacs tree with modifications.  NOT a separate GUI
backend (unlike the Mac port).  Uses the standard NS (Cocoa) port
with conditional `#ifdef AQUAMACS` blocks and a large Elisp overlay.

### C Source Changes (minimal, ~15 conditional blocks total)

- `src/nsaquamacs.m` (1,341 lines) -- **New file**, 26 DEFUN
  functions for macOS integration
- `src/nsaquamacs.h` -- Header for the above
- `src/nsterm.m` -- 5 `#ifdef AQUAMACS` blocks (branding, color
  lists, menu names, resizing hints, frame management)
- `src/nsfns.m` -- 2 small patches (NSCalibratedRGBColorSpace)
- `src/emacs.c` -- Binary name, `syms_of_nsaquamacs()` init
- `configure.ac` -- App bundle naming, nsaquamacs.o in build

### Elisp Overlay (`aquamacs/src/site-lisp/`)

~40+ custom Elisp files providing the bulk of customization:
- `one-buffer-one-frame.el` -- Each buffer gets its own window
- `smart-frame-positioning.el` -- Remembers frame positions
- `osxkeys.el` -- Full macOS keybindings (Cmd-S/C/V/Z)
- `emulate-mac-keyboard-mode.el` -- Option as Meta preserving
  special character input
- `aquamacs-editing.el` -- CUA mode, Mac clipboard behavior
- `aquamacs-tool-bar.el` / `aquamacs-menu.el` -- Mac-style UI
- `aquamacs-autoface-mode.el` -- Per-mode font customization
- `tabbar/` -- Tab bar for buffer switching
- `mac-print.el` -- Native printing support
- `smart-dnd.el` -- Mode-aware drag-and-drop
- `check-for-updates.el` -- Auto-update checking

### Bundled Third-Party Packages

AUCTeX, ESS, MATLAB mode, AppleScript mode, nxhtml, paredit,
markdown-mode, and others.  Mostly obsolete now that ELPA/MELPA
exist.

## C Primitives in nsaquamacs.m (26 functions)

### Spellchecker (11 functions) -- NSSpellChecker API
- `ns-popup-spellchecker-panel`
- `ns-spellchecker-check-spelling`
- `ns-spellchecker-check-grammar`
- `ns-spellchecker-get-suggestions`
- `ns-spellchecker-learn-word` / `ns-spellchecker-ignore-word`
- `ns-spellchecker-list-languages` / `ns-spellchecker-set-language`
- Others for counts and completions

### Printing/Rendering
- `ns-popup-page-setup-panel` / `ns-popup-print-panel`
- `ns-popup-save-panel` (sheet-style)
- `aquamacs-html-to-rtf` / `aquamacs-render-to-pdf`

### System Integration
- `ns-os-version`
- `ns-send-odb-notification` (XCode/ODB)
- `ns-application-hidden-p`
- `ns-launch-URL-with-default-browser`
- `ns-open-help-anchor` (Apple Help)
- `ns-cycle-frame` / `ns-visible-frame-list`
- `ns-frame-is-on-active-space-p` (Spaces awareness)

## Absorb verdict (downstream — into `jylhis/emacs`)

Aquamacs is not patch-based (it carries a large Elisp overlay plus
`#ifdef AQUAMACS` source blocks against Emacs 29.4), so the
patch-source poll cannot track it mechanically.  Below is a manual
candidate list.  Each candidate would need forward-porting from 29.4
to this fork's 31.0.50 base and stripping the `AQUAMACS` ifdefs.

| Candidate | Verdict | Why |
|---|---|---|
| NSSpellChecker primitives (11 DEFUNs in `src/nsaquamacs.m`) | **defer (separate workstream)** | Substantive feature gap in the NS port; clean API design but ~1300 lines plus a new source file.  File under `fork-todos.md` as its own track. |
| NSCalibratedRGBColorSpace fix in `src/nsfns.m` | **verify-then-absorb** | Trivial change; verify against this fork's current `src/nsfns.m` colorspace handling before applying. |
| `ns-frame-is-on-active-space-p`, `ns-visible-frame-list` | **defer** | Useful for macOS Spaces awareness, but tied to Aquamacs' frame-tracking model; needs reimplementation, not a port. |
| Native print/page-setup sheet dialogs | **defer** | Better UX than the current NS print path but non-trivial; queue behind NSSpellChecker. |
| Copy as RTF/PDF | **not-applicable** | Uses WebKit; design controversy + adds a heavyweight dep. |
| Smart frame positioning | **not-applicable** | Aquamacs-specific runtime model. |
| One-buffer-one-frame, `osx-key-mode`, bundled packages | **not-applicable** | Distribution-level decisions outside the source. |

## Polling

Not tracked by the patch-source poll by default — see the seed
manifest in `attributes/patch-sources.toml` (the `aquamacs` source is
commented out).  Aquamacs ships diffs only as branches against
upstream; tracking would require a separate git-diff workflow, and
the candidate list above is the manual replacement.
