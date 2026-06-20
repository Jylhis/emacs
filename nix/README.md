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

Variants (overlay attrs / flake packages): `emacs` (default, full AOT),
`emacs-nox`, `emacs-pgtk`, `emacs-gtk3`, `emacs-macos`, and `emacs-core`
(lighter — see below).

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
| `extraProfilePackages` | Extra packages installed alongside (tools on PATH for the daemon) |
| `defaultEditor` | Set `EDITOR=emacsclient` |
| `daemon.enable` | Run `emacs --fg-daemon` as a user service |
| `daemon.extraOptions` | Extra daemon args |

## Caching: what works, and what doesn't

Native compilation of the `lisp/` tree dominates build time. The obvious idea —
split the core from the rest of the `.eln` and cache them independently — was
tried and **does not work** here. Measured on this tree:

- `emacs` (full AOT): 3011 `.eln`.
- `emacs-core` (default mode): 1667 `.eln`.

The build already AOT-compiles every preloaded/loaded-at-build library (1667)
to produce a working dumped Emacs; that set can't be deferred. A separate
"compile the remaining lisp" derivation is defeated by three things: the
installed lisp is gzip-compressed (`compress-install`), `.eln` filenames are
hashed from the source's **absolute path and content** (so eln compiled
elsewhere aren't found at runtime), and `load--fixup-all-elns` rewrites
references after install. Even if forced to work, `emacs-core` still recompiles
1667 `.eln` on *any* source change, so the incremental saving is small.

So Nix derivations cannot give an incremental core/lisp split. The caching
levers that **do** work:

- **Cachix** — build once, substitute everywhere. Push the package outputs;
  other machines and CI pull instead of building.
- **`emacs-core`** — a genuinely lighter target: ~45% fewer `.eln`, faster to
  build, smaller closure. The deferred libraries native-compile on first use
  (JIT) into the user's eln-cache. Good for CI and constrained machines; it is
  *not* an incremental-rebuild mechanism.
- **Third-party Elisp packages** are already separate derivations via
  `emacsPackagesFor`; adding one never rebuilds Emacs.
- **The dev shell** is the real answer for iteration — see below.

**For true file-level incrementality** (editing one file → only its dependents
rebuild), Nix cannot help — use the dev shell, where Emacs's own Makefiles do
incremental rebuilds and ccache makes C recompiles near-instant:

```sh
nix develop
./autogen.sh
./configure --with-native-compilation=default
make -j$(nproc)        # edit a file, re-run make
```
