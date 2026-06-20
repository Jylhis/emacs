# Nix packaging for this Emacs checkout

This directory packages the working tree with Nix: a flake that builds Emacs
from `./.`, NixOS / home-manager / nix-darwin modules that can run the daemon,
and a build split for caching efficiency. The upstream Autotools build is used
as-is (this layer reuses the nixpkgs Emacs builder); nothing here replaces the
build system.

## Layout

| File | Purpose |
|---|---|
| `../flake.nix` | Inputs, packages, overlay, modules, devShell, formatter |
| `package.nix` | Core derivation — `nixpkgs` Emacs builder, `src = ./.`, `autogen.sh` |
| `src-filter.nix` | Clean-source filter (drops `.git`, build artifacts, `nix/`) |
| `overlay.nix` | `emacs-jylhis*` variants + the core/native-lisp split |
| `native-lisp.nix` | Separate AOT `.eln` derivation for the split |
| `lib.nix` | `emacsPackagesFor` / `withPackages` / use-package helpers |
| `devshell.nix` | Incremental `make` dev shell (ccache on Linux) |
| `modules/` | `programs.emacs-jylhis` for NixOS, home-manager, nix-darwin |
| `treefmt.nix` | nixfmt / deadnix / statix for the Nix sources |

## Quick start

```sh
nix build .#emacs        # default GUI build (pgtk on Linux, NS on macOS)
nix run   .#emacs        # build and run
nix build .#emacs-nox    # terminal build
nix develop              # dev shell for incremental `make`
```

Variants (overlay attrs / flake packages): `emacs` (default), `emacs-nox`,
`emacs-pgtk`, `emacs-gtk3`, `emacs-macos`, plus the split pair `emacs-core` /
`emacs-native-lisp`.

## Modules

All three expose `programs.emacs-jylhis`. Apply the overlay so
`pkgs.emacs-jylhis` exists, then:

```nix
# NixOS / nix-darwin
{ inputs, pkgs, ... }: {
  nixpkgs.overlays = [ inputs.emacs-jylhis.overlays.default ];
  imports = [ inputs.emacs-jylhis.nixosModules.default ];   # or .darwinModules.default
  programs.emacs-jylhis = {
    enable = true;
    daemon.enable = true;     # systemd user service / launchd agent: emacs --fg-daemon
    defaultEditor = true;     # EDITOR=emacsclient
    extraPackages = epkgs: [ epkgs.magit epkgs.vertico ];
  };
}
```

home-manager is the same under `inputs.emacs-jylhis.homeManagerModules.default`.

| Option | Meaning |
|---|---|
| `enable` | Install the build |
| `package` | Which variant (default `pkgs.emacs-jylhis`) |
| `extraPackages` | `epkgs: [ ... ]` Elisp packages |
| `extraProfilePackages` | Co-installed packages — set `[ pkgs.emacs-jylhis-native-lisp ]` with `emacs-jylhis-core` |
| `defaultEditor` | Set `EDITOR=emacsclient` |
| `daemon.enable` | Run `emacs --fg-daemon` as a user service |
| `daemon.extraOptions` | Extra daemon args |

## Caching and the build split

Native compilation of the full `lisp/` tree (~2k `.eln`) dominates build time.
Nix derivations are atomic on their source, and the C core + preloaded Lisp +
`pdmp` dump are one coupled unit, so the core cannot be losslessly sub-divided.
What *is* separable — and is the expensive part — is the non-preloaded `.eln`
tree:

- **`emacs-jylhis-core`** builds native-compilation in *default* mode (only the
  preloaded Lisp is AOT-compiled; `NATIVE_FULL_AOT` is dropped). A C change
  rebuilds only this — it never recompiles the whole `.eln` tree.
- **`emacs-jylhis-native-lisp`** AOT-compiles the rest against the core binary
  into its own `share/emacs/native-lisp/<abi>/`. `nixpkgs` `site-start.el`
  unions that across `NIX_PROFILES`, so co-installing both
  (`extraProfilePackages`) yields full AOT coverage with the two halves cached
  independently. A Lisp change rebuilds only this half.
- Third-party Elisp packages are already separate derivations via
  `emacsPackagesFor`; adding one never rebuilds Emacs.

Push `emacs-core` and `emacs-native-lisp` to Cachix and machines substitute the
expensive halves instead of building.

**For true file-level incrementality** (editing one file → only its dependents
rebuild), Nix cannot help — use the dev shell, where Emacs's own Makefiles do
incremental rebuilds and ccache makes C recompiles near-instant:

```sh
nix develop
./autogen.sh
./configure --with-native-compilation=default
make -j$(nproc)        # edit a file, re-run make
```
