# Emacs Mac Port (Mitsuharu Yamamoto)

Alternative macOS GUI backend for GNU Emacs, maintained since the
Carbon era (~2005).  Replaces the NS (Cocoa) port entirely with a
parallel implementation using macOS-native APIs.

## Repositories

- **Upstream**: https://bitbucket.org/mituharu/emacs-mac
  - Maintainer: YAMAMOTO Mitsuharu (mituharu@math.s.chiba-u.ac.jp)
  - Current release: emacs-29.4-mac-10.1 (2025-03-31)
  - Development has slowed; `work` branch last updated 2025-09-20
- **Community continuation**: https://github.com/jdtsmith/emacs-mac
  - Maintainer: jdtsmith + community
  - Branches: `emacs-mac-30_1_exp` (Emacs 30), `emacs-mac-gnu_master_exp` (master/31)
  - Actively maintained (last push 2026-04-25), 136 stars

## Architecture

Full Emacs tree with a **parallel GUI backend** (`--with-mac`).
Not a patch set on the NS port.  Adds entirely new source files:

    src/macterm.c      (equivalent of nsterm.m)
    src/macfns.c       (equivalent of nsfns.m)
    src/macmenu.c      (equivalent of nsmenu.m)
    src/macselect.c    (equivalent of nsselect.m)
    mac/               (Objective-C sources, nibs, resources)
    lisp/term/mac-win.el  (equivalent of ns-win.el)

None of these files exist in GNU Emacs.  Uses Objective-C blocks
and macOS-only APIs (Core Text, Core Animation, Image I/O, GCD)
that require Clang -- incompatible with GCC, which is a policy
blocker for upstream GNU Emacs (GNUstep compatibility requirement).

## Key Features vs NS Port

- **Reliable C-g** -- interrupts long Lisp without menu bar activation
- **Zero CPU idle** -- efficient select() emulation, no periodic polling
- **Graceful logout/shutdown** -- confirmation dialogs, cancelation support
- **Apple Events at Lisp level** -- mailto:, ODB Editor Suite, etc.
- **Trackpad gestures** -- pinch to zoom, swipe for buffer switching
- **Smooth pixel scroll** -- native trackpad pixel-level events
- **Retina @2x support** -- automatic high-DPI image handling
- **SVG via WebKit** -- no librsvg dependency needed
- **Core Animation** -- `mac-start-animation` for buffer transitions
- **DictionaryService** -- Cmd-Ctrl-D word lookup
- **Right-side modifier keys** -- independently mappable
- **Color bitmap fonts** -- Apple Color Emoji with skin tone modifiers
- **Metal rendering** -- optional `--with-mac-metal`
- **Accessibility framework** support for custom views

## jdtsmith-Specific Additions

Features:
- "New Frame" Dock menu entry
- Full-featured Window menu (tabs, tiling, system shortcuts)
- `mac-raise-all-frames`, `mac-toggle-frame-full-screen`
- `mac-underwave-thickness` custom variable

Bug fixes:
- Font panel crash prevention
- Zombie "Emacs Web Content" processes on SVG load
- Hangs on dying thread callbacks, waking from sleep
- GCD deadlock on sync queue draw
- Stale Core Graphics context
- `CF|NS_NOESCAPE` normalization for non-system Clang
- Do not use XGSELECT even if HAVE_GLIB
- Defer updating presentation options during FullScreen teardown

## Cherry-Pick Feasibility

**Not feasible.**  The Mac port is architecturally incompatible:
- Commits modify files (macterm.c, etc.) that don't exist upstream
- Requires Clang (blocks syntax) -- violates GCC compatibility policy
- FSF copyright assignment not in place for Yamamoto's code
- Would require complete reimplementation to land in the NS port

A few shared-code fixes have already been upstreamed (e.g.,
bug#80851 SVG off-by-one).  The XGSELECT change may be
Mac-port-specific.

## Value for Upstream Work

The Mac port is best used as **reference implementation** when
improving the NS port.  Features like reliable C-g, zero-CPU idle,
and gesture support could be reimplemented in nsterm.m/nsfns.m
using NS-compatible (GCC-friendly) APIs.
