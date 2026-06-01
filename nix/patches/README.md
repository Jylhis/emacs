# macOS Patches

This directory holds optional patches mirrored from
[homebrew-emacs-plus](https://github.com/d12frosted/homebrew-emacs-plus)
that polish the macOS Cocoa NS build.

The package's `withSystemAppearancePatch` and
`withRoundUndecoratedPatch` arguments check for the presence of the
corresponding `.patch` file here before applying it, so an empty
directory means the patches are simply unavailable; consumers can drop
patch files in without modifying `package.nix`.

## Expected files

| Filename                          | Source (emacs-plus, Emacs 31 series)               |
|-----------------------------------|----------------------------------------------------|
| `system-appearance.patch`         | `patches/emacs-31/system-appearance.patch`         |
| `round-undecorated-frame.patch`   | `patches/emacs-31/round-undecorated-frame.patch`   |

## Provenance and drift

These patches target stock GNU Emacs.  This fork has independent NS
work in `src/nsterm.m` and `src/nsfns.m`; verify each patch applies
cleanly with `git apply --check nix/patches/<name>.patch` before
flipping the corresponding flag on for production use.

See `.claude/notes/fork-homebrew-emacs-plus.md` and
`.claude/notes/fork-nix-darwin-emacs.md` for the downstream-tracking
records that drive when these patches should be refreshed.
