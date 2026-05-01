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

## Cherry-Pick Feasibility

**No patches applicable to upstream GNU Emacs.**  The sole current
patch (`native-comp-driver-options-30.patch`) is Nix-specific
plumbing.  Historical patches were for bugs that have since been
fixed upstream.

The overlay is useful as a **downstream consumer reference** --
it tracks which upstream bugs affect real users (the issues/PRs
document breakage that Nix users hit first due to building from
HEAD daily).  Bug numbers referenced: #67916, #63288, #76523.
