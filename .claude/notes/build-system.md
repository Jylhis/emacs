# Build System Notes

Sources: INSTALL, INSTALL.REPO, nextstep/INSTALL, etc/DEBUG,
admin/README, admin/make-emacs, admin/quick-install-emacs.

## Branch state: Meson + Ninja only

The autotools entry points were removed at phase-10 cutover (commit
`313f867`).  See `/root/.claude/plans/review-current-meson-based-merry-fairy.md`
for the post-cutover parity audit and the prioritised work plan.

## Meson build

    meson setup build -Dnative-compilation=yes
    meson compile -C build
    build/src/emacs --batch --eval '(princ (* 6 7))'   # -> 42
    meson test -C build --suite smoke
    meson install -C build --destdir=/tmp/stage

Bootstrap dance (custom_targets):

    libgnu (lib/)              # gnulib subset
    lib-src/* (8 helpers)      # make-docfile, etags, emacsclient, ...
    temacs                     # undumped, bootstrap host
    bootstrap-emacs            # cp of temacs
    unidata-stamp              # uni-*.el + charprop.el
    bootstrap-emacs.pdmp       # initial pdumper image
    loaddefs-stamp             # autoload extraction
    compile-first / compile-main  # byte-compile lisp/
    native-lisp-stamp          # .eln (with -Dnative-compilation=yes)
    emacs / emacs.pdmp         # final pdumped image

## First-time autotools build (legacy on this branch)

    ./autogen.sh    # generates configure (needs autoconf, git, texinfo)
    ./configure
    make

Or as a single command:

    make            # GNUmakefile auto-runs autogen.sh + configure

Pass custom configure flags via:

    make configure="--prefix=/opt/emacs CFLAGS='-O0 -g3'"

## Debug build (etc/DEBUG recommendation)

    ./configure --enable-checking='yes,glyphs' \
                --enable-check-lisp-object-type \
                CFLAGS='-O0 -g3'

- `-O0` is critical; even `-Og` has known GCC bugs (#78685).
- `--enable-checking` adds runtime assertion checks and display
  debugging commands.
- `--enable-check-lisp-object-type` catches Lisp_Object type misuse
  at compile time.

## macOS / NS build (nextstep/INSTALL)

On macOS, `--with-ns` is the default.  After `make`, run:

    make install    # assembles nextstep/Emacs.app

The `--prefix` flag has no effect for NS builds; instead move
`nextstep/Emacs.app` wherever you want.

To target older macOS versions:

    CFLAGS="-DMAC_OS_X_VERSION_MIN_REQUIRED=1060 ..."

## Bootstrap vs incremental

- `make` -- incremental rebuild.
- `make bootstrap` -- full clean + rebuild.  Accepts configure= var.
- `make bootstrap configure=default` -- bootstrap with default options.

## Out-of-tree builds

    mkdir ../emacs-build && cd ../emacs-build
    /path/to/emacs/configure
    make

Useful for testing different configurations without polluting the
source tree.

## Parallel make

- `make -j$(nproc)` for building -- safe and recommended.
- `make check` must NOT use `-j` -- parallel tests cause flaky failures.

## admin/emake -- quiet build + auto-test

    ./admin/emake              # build with reduced noise, auto-test changed files
    ./admin/emake --quieter    # only show errors/warnings
    ./admin/emake --no-check   # skip auto-testing

Highlights errors in red.  Runs `make check-maybe` to test only files
that changed since last build.

## admin/quick-install-emacs -- incremental install

Uses hard-links for fast installs.  Only updates changed files.
Intended for frequent re-installs during development.

    ./admin/quick-install-emacs BUILD_TREE [PREFIX]

## Key configure options for development

    --without-all --without-x          # minimal build for fast iteration
    --with-native-compilation=aot      # AOT compile all Lisp
    --with-native-compilation=no       # disable native comp
    --with-modules                     # dynamic module support
    --enable-gcc-warnings              # treat warnings as errors
    --enable-gcc-warnings=warn-only    # warnings only, no errors
    --with-pgtk                        # Pure GTK (Wayland/Broadway)
    --with-cairo                       # Cairo drawing
    --enable-link-time-optimization    # LTO (slower, crash-prone)

## Parked / unsupported

These platform backends from the autotools tree have intentionally
not been ported to Meson; the fork prioritises Linux GTK3, Linux
terminal, and macOS NS/terminal.  Reviving any of them means
porting the platform-specific C/Java code, not just translating a
Makefile -- the work is a port, not a migration.

| Backend | Autotools recipe (at anchor `08a22b8965ec`) | Why parked |
|---|---|---|
| Android cross-build | `java/Makefile.in`, `exec/Makefile.in`, `cross/Makefile.in`, `cross/ndk-build/Makefile.in` | Thousands of lines of NDK + Java glue.  Re-introduces a parallel build system. |
| Windows GUI / Cygwin | `nt/`, configure.ac w32 / native-image-api / cygwin32-native-compilation switches | C backend not on this fork's roadmap. |
| Haiku | configure.ac be-app / be-cairo switches | Same. |
| `admin/grammars/` | `admin/grammars/Makefile.in` | Outputs are committed to `lisp/cedet/semantic/`; only matters when editing `.by`/`.wy` source grammars. |
| `lib-src/asset-directory-tool` | `lib-src/Makefile.in:418` | Android-only. |
| `xaw3d` / Motif / Lucid X toolkits | configure.ac toolkit selector | Already dropped per `meson.options:52-53`. |
| `gconf` | configure.ac AC_ARG_WITH | Deprecated; option `disabled` by default. |
| `imagemagick` | configure.ac AC_ARG_ENABLE | `disabled` by default; security advisories argue against turning back on. |

To revive a parked backend, start by `git show 08a22b8965ec:<path>`
and translate the rules into a new Meson `subdir()` block.  Update
`meson.build`'s parked-subdirs list and `meson.options` (which
keeps a stub list of parked option names) when promoting one.

## Release pipeline

Tag-driven multi-platform releases run from
`.github/workflows/release.yml`.  The full process (tag scheme, what
ships, how to cut a release, how to verify) is documented in
`admin/jylhis-release-process.md`.

Targets, as of the first cut:

- Linux x86_64 + aarch64, three GUI variants each (`gtk3` for X11,
  `pgtk` for Wayland, `nox` for terminal-only) -- shipped as
  `tar.xz` of the `meson install --destdir` tree.
- macOS universal `.dmg`: x86_64 + arm64 `Emacs.app` bundles merged
  with `lipo` via `admin/build-darwin-universal.sh`, then ad-hoc
  signed (no Apple Developer ID yet).
- Nix flake outputs for every system/variant declared in `flake.nix`
  (best-effort -- doesn't gate the release).
- Android: parked (see table above).  The workflow emits a
  placeholder `ANDROID_STATUS.md` in the release notes.
