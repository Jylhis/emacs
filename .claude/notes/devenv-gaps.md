# DevEnv Gaps

Packages and scripts that the upstream documentation recommends but
are not yet in devenv.nix.

## Missing packages

| Package | Why | Source |
|---------|-----|--------|
| codespell | `admin/run-codespell` spell-checks the tree | admin/README |
| coccinelle | Semantic C patches in `admin/coccinelle/` | admin/coccinelle/README |
| tree-sitter | Grammar compatibility testing | admin/tree-sitter/ |
| libgccjit | Native Lisp compilation (--with-native-compilation) | INSTALL |
| harfbuzz | Complex text layout (recommended over m17n) | INSTALL |
| librsvg | SVG image support | INSTALL |
| libwebp | WebP image support | INSTALL |
| libjpeg | JPEG image support | INSTALL |
| libtiff | TIFF image support | INSTALL |
| giflib | GIF image support | INSTALL |
| libpng | PNG image support | INSTALL |
| zlib | Required by libpng | INSTALL |
| libxpm | XPM image support (X11 only) | INSTALL |
| dbus | D-Bus support | INSTALL |
| ImageMagick | Optional, disabled by default | INSTALL |

Note: on macOS with NS build, X11 image libraries are not needed --
Cocoa frameworks handle images natively.  The libraries above matter
primarily for X11/GTK builds.

## Missing convenience scripts

| Script | Purpose |
|--------|---------|
| emacs-emake | Wraps `admin/emake` for quiet build + auto-test |
| emacs-codespell | Wraps `admin/run-codespell` |
| emacs-test-file | Single-file test: `make -C test lisp/$1-tests` |
| emacs-bisect | Wraps `admin/git-bisect-start` |
| emacs-ns-install | macOS: `make install` + note about Emacs.app location |
| emacs-debug | Launches `gdb` or `lldb` from src/ with correct paths |

## GDB/LLDB auto-load setup

etc/DEBUG recommends adding to ~/.gdbinit:

    add-auto-load-safe-path /path/to/emacs/src/.gdbinit

This could be done via an enterShell hook in devenv.nix, or
documented as a one-time manual step.

## Out-of-tree build support

INSTALL recommends out-of-tree builds for testing different
configurations.  A script wrapping this pattern would be useful:

    mkdir -p build && cd build && ../configure [opts] && make -j$(nproc)
