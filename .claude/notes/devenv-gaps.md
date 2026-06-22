# DevEnv Gaps

Packages and scripts that the upstream documentation recommends but
are not yet in devenv.nix.

## Status (updated 2026-06-01, JYL-28)

Most gaps have been filled.  Remaining items noted below.

## Package status

| Package | Why | Status |
|---------|-----|--------|
| codespell | `admin/run-codespell` spell-checks the tree | **Added (JYL-28)** |
| coccinelle | Semantic C patches in `admin/coccinelle/` | **Added (JYL-28)** |
| libxpm | XPM image support (X11 only) | **Added (JYL-28)** |
| tree-sitter | Grammar compatibility testing | Present (added earlier) |
| libgccjit | Native Lisp compilation | Present, Linux-only (added earlier) |
| harfbuzz | Complex text layout | Present (added earlier) |
| librsvg | SVG image support | Present (added earlier) |
| libwebp | WebP image support | Present (added earlier) |
| libjpeg | JPEG image support | Present (added earlier) |
| libtiff | TIFF image support | Present (added earlier) |
| giflib | GIF image support | Present (added earlier) |
| libpng | PNG image support | Present (added earlier) |
| zlib | Required by libpng | Present (added earlier) |
| dbus | D-Bus support | Present, Linux-only (added earlier) |
| ImageMagick | Optional, disabled by default | Intentionally omitted (optional, disabled) |

## Convenience scripts

| Script | Purpose | Status |
|--------|---------|--------|
| emacs-run | Launch locally built Emacs -Q | Present (added earlier) |
| emacs-run-installed | Launch installed Emacs -Q | Present (added earlier) |
| meson-setup | Configure meson build dir | Present (added earlier) |
| meson-build | Build all Meson targets | Present (added earlier) |
| meson-pdmp | Run full dump cycle | Present (added earlier) |
| emacs-test-file | Single-file ERT test runner | **Added (JYL-28)** |
| emacs-codespell | Wraps `admin/run-codespell` | **Added (JYL-28)** |
| emacs-bisect | Wraps `admin/git-bisect-start` | **Added (JYL-28)** |
| emacs-debug | Launches GDB/LLDB from src/ | **Added (JYL-28)** |
| emacs-emake | Wraps `admin/emake` | N/A — Meson-only fork, no emake |
| emacs-ns-install | macOS: make install + Emacs.app note | Not yet added |

## GDB/LLDB auto-load setup

`emacs-debug` script now launches from `src/` which auto-loads `src/.gdbinit`.
One-time manual step still needed to add to `~/.gdbinit`:

    add-auto-load-safe-path /path/to/emacs/src/.gdbinit

## Out-of-tree build support

Not applicable: this fork supports in-tree builds only (Meson + Ninja).
`build/` is the conventional out-of-tree build dir.
