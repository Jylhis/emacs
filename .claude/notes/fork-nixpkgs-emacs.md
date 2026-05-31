# NixOS/nixpkgs — `pkgs/applications/editors/emacs/`

Canonical home of Nix's mainline-Emacs patches.  Polled by the
`upstream-commit-review` skill (source: `nixpkgs-emacs`).

## Repository

- https://github.com/NixOS/nixpkgs
- Branch: `master`
- Glob: `pkgs/applications/editors/emacs/*.patch` (flat directory, no
  `patches/` subdir)

## Patch model

`nixpkgs` ships `.patch` files directly in the Emacs derivation
directory.  These are applied during the Nix build via the standard
`patches = [ ... ]` derivation attribute.

The closely-related `nix-community/emacs-overlay` repo carries **no**
`.patch` files of its own — it imports the relevant patches from
nixpkgs.  So this source is the right place to watch for new Nix
plumbing patches.

## Verdict expectations

Almost all patches here are Nix-sandbox plumbing (native-comp driver
options, store-path injection, lexical-cookie warnings the Nix CI
trips on).  Default verdict for new rows: `not-applicable` — they
configure Nix-specific build details that don't transfer to a
non-sandboxed build.

The exception is the occasional Bug# fix that lands here before
upstream merges it (e.g. `inhibit-lexical-cookie-warning-67916-30.patch`
which referenced Bug#67916, eventually fixed upstream).  These are
short-lived; the file disappears when upstream lands the fix.

## Tracked patches (as of 2026-05-31)

| Patch | Verdict | Note |
|---|---|---|
| `native-comp-driver-options-30.patch` | `not-applicable` | Injects Nix store paths into `native-comp-driver-options` so libgccjit finds linker/SDK/libs inside the sandbox.  Non-Nix builds use system paths. |
| `inhibit-lexical-cookie-warning-67916-30.patch` | `not-applicable` | Bug#67916 — Already absorbed upstream; nixpkgs slated to remove this when their pinned Emacs rolls forward. |

## Related fork notes

- [[fork-nix-emacs-overlay]] — upstream community overlay; consumes
  patches from this repo via `nix-community/emacs-overlay/repos/nixpkgs`.
- [[fork-nix-darwin-emacs]] — `nix-giant/nix-darwin-emacs`; the Darwin-
  specific overlay polled separately.
