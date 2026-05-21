# nix-community/emacs-overlay

Nix overlay providing bleeding-edge Emacs builds and package sets
for Nixpkgs.  The standard way to get latest Emacs on NixOS/nix-darwin.

## Repository

- https://github.com/nix-community/emacs-overlay
- 615 stars, 183 forks, primary maintainer: @adisbladis
- Extremely active -- automated updates every 8 hours via CI

## Emacs Variants Provided

| Attribute          | Source            | Notes                |
|--------------------|-------------------|----------------------|
| emacs-git          | master (daily)    | X11/NS               |
| emacs-git-pgtk     | master (daily)    | Pure GTK (Wayland)   |
| emacs-git-nox      | master (daily)    | No GUI               |
| emacs-unstable     | Latest tag (30.2) | Latest release       |
| emacs-unstable-pgtk| Latest tag        | Release + pure GTK   |
| emacs-unstable-nox | Latest tag        | Release, no GUI      |
| emacs-igc          | feature/igc3      | Incremental GC (MPS) |
| emacs-igc-pgtk     | feature/igc3      | IGC + pure GTK       |

Also provides daily-updated MELPA, GNU ELPA, NonGNU ELPA packages.

## Current Patches (as of 2026-04-27)

### native-comp-driver-options-30.patch

**Nix-specific, NOT for upstream.**  File: `lisp/emacs-lisp/comp.el`

Injects Nix store paths into `native-comp-driver-options` so
`libgccjit` can find the linker, assembler, and system libraries
inside the Nix sandbox.  Uses `@backendPath@` placeholder
substituted at build time with paths to libgccjit, libc, libgcc,
cc, bintools, and on Darwin the Apple SDK.

Applied to: emacs-git, emacs-git-pgtk, emacs-igc, emacs-igc-pgtk.
NOT applied to emacs-unstable (uses nixpkgs upstream patch).

### Recently Removed Patches

- **inhibit-lexical-cookie-warning-67916-30.patch** (removed
  2026-04-27) -- Bug#67916, skipped lexical-binding cookie
  warning for `-pkg.el` files.  Upstream fixed.

- **bytecomp-revert.patch** (removed 2025-03-08) -- Bug#63288,
  Bug#76523, byte compiler regression.  Upstream fixed.

## Build Modifications

- `--enable-check-lisp-object-type` on aarch64-linux (fixes
  segfaults, issue #264)
- Git revision/branch injection into `lisp/loadup.el`
- IGC variants: `mps` build input + `--with-mps=yes`
- Tramp 2.8.0.4 tarball workaround (pinned to 2.8.0.3)

## Absorb verdict (downstream — into `jylhis/emacs`)

**No patches to absorb.**  `native-comp-driver-options-30.patch` is
Nix-specific plumbing — it substitutes Nix store paths
(`@backendPath@`) into `native-comp-driver-options` so libgccjit can
find its toolchain inside the Nix sandbox.  Outside the Nix sandbox
the substitution is meaningless; outside libgccjit it does nothing.

Historical patches were for bugs that have since been fixed upstream
(bug#67916, bug#63288, bug#76523) and removed from the overlay — no
work needed here.

## Reference value

Still useful as a **downstream consumer canary**: the overlay's CI
builds master daily, so when upstream master breaks the Nix build,
this overlay's issue tracker is where users surface it first.  Watch
for new entries in the overlay's `patches/` directory — a re-added
patch usually means upstream regressed something that affects sandbox
builds.

## Polling

Not tracked by the patch-source poll by default.  The single Nix-only
patch wouldn't trigger any `absorb-now` verdicts and would just add
noise to the report.  If a non-Nix-specific patch ever appears,
re-evaluate and add a manifest entry then.
