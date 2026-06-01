# Build System Notes

Sources: INSTALL, INSTALL.REPO, nextstep/INSTALL, etc/DEBUG,
admin/README, admin/make-emacs, admin/quick-install-emacs.

## Branch state: Meson + Ninja only

The autotools entry points were removed at phase-10 cutover (commit
`313f867`).  See `/root/.claude/plans/review-current-meson-based-merry-fairy.md`
for the post-cutover parity audit and the prioritised work plan.

### Phase numbering

`git log --oneline --grep="Meson migration phase"` shows commits for
phases 1, 2, 3, 4, 5, 6, 7, and 10; phase 9 lands at `2bf867f8398`
("Phase 9: refresh top-level docs for the dropped platforms").
Phase 8 has no matching commit title -- it was either silently
rolled into the surrounding lib-src buildup or skipped.  The
numbering is preserved for historical traceability rather than
self-documentation; do not assume phase N+1 follows phase N
strictly.

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

### Byte-compile skips (the "N skipped (compile errors)" line)

`meson/byte_compile_batch.py` prints `byte-compiled N files; M skipped
(compile errors)` and always exits 0, so byte-compile failures are silent
-- the file just never gets a `.elc` (nor a `.eln`) and Emacs falls back
to source at runtime.  This masked a large regression: the build reported
**140 skipped**.  Root causes, in the order they bite:

1. **cl-extra functions void at compile time** (was ~115 files, incl. the
   whole `cedet/` tree, css-mode, ox-*, window-tool-bar).  The compiler is
   `bootstrap-emacs` running `bootstrap-emacs.pdmp`, which is dumped with
   `--temacs=pbootstrap` *before* `loaddefs-stamp` generates
   `cl-loaddefs.el` (loaddefs-stamp depends on bootstrap_pdmp).  At dump
   time `cl-lib.el`'s `(load "cl-loaddefs")` fails and its fallback loads
   `cl-macs`+`cl-seq` but deliberately **not** `cl-extra`; `cl-lib` is then
   already `provide`d, so a file's own `(require 'cl-lib)` is a no-op and
   the `cl-extra` autoloads (`cl-every`, `cl-some`, `cl-mapl`, `cl-subseq`,
   ...) never register.  Fix: `byte_compile_batch.py` loads `cl-loaddefs`
   in the compile session.  Fixing this exposed a load-path collision --
   with `cedet/srecode/compile.elc` now built, a bare `(require 'compile)`
   found it instead of `progmodes/compile`.  cedet sub-packages are
   reachable via their slash-prefixed features through the `cedet` entry
   alone, so `_load_path` now drops the nested `cedet/*` directories.

2. **`no-byte-compile: t` missed** (23 files: `international/uni-*.el`,
   `charprop.el`, `ldefs-boot.el`, `loadup.el`, `theme-loaddefs.el`,
   `org/org-version.el`).  These carry the cookie in a trailing
   `Local Variables:` block; `list_lisp_files.py` inspected only the first
   line, so they entered the manifest and `batch-byte-compile` correctly
   refused them -- miscounted as errors.  Fix: scan both ends of the file.

After both fixes: **25 residual skips**, a *separate* pre-existing gap, not
cl-related:
- ~20 CEDET files need generated grammar outputs (`semantic/bovine/*-by`,
  `semantic/wisent/*-wy`, `srecode/srt-wy`) that are **absent from the
  tree** (0 on disk, 0 git-tracked).  NB: the parked-backends table below
  claims `admin/grammars/` outputs "are committed to lisp/cedet/semantic/"
  -- that is currently false; reviving CEDET fully needs the grammar
  generation (`.wy`/`.by` -> `*-wy.el`/`*-by.el`) wired into Meson.
- 4 obsolete files (`obsolete/idlw*`, `isearchb`->`iswitchb`) fail because
  `obsolete/` is excluded from the byte-compile load path.
- `international/textsec.el` needs the generated `uni-confusable.el`.

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

## Supported platforms

The fork commits to three platform families:

- **Linux**: x86_64 and aarch64, three GUI variants each (gtk3, pgtk,
  nox).  Built natively by the release workflow.
- **macOS**: x86_64 (Intel) and arm64 (Apple Silicon).  Shipped as a
  universal `.dmg`.
- **Android**: arm only (armeabi-v7a + arm64-v8a).  Source for the
  port stays in-tree under `java/`, `exec/`, `cross/ndk-build/`, and
  `src/android*`; the Meson recipe to drive the cross-build is still
  a TODO.  Until that lands, the Android job in `release.yml` is a
  placeholder.

## Parked / unsupported

These platform backends from the autotools tree have intentionally
not been ported to Meson; the fork prioritises Linux, macOS, and
Android.  Reviving any of them means porting the platform-specific
C/Java code, not just translating a Makefile -- the work is a port,
not a migration.

| Backend | Autotools recipe (at anchor `08a22b8965ec`) | Why parked |
|---|---|---|
| Windows GUI / Cygwin | `nt/` and `lib-src/ntlib*` (both deleted upstream), configure.ac w32 / native-image-api / cygwin32-native-compilation switches | C backend not on this fork's roadmap. |
| Haiku | configure.ac be-app / be-cairo switches | Same. |
| `admin/grammars/` | `admin/grammars/Makefile.in` | Outputs are committed to `lisp/cedet/semantic/`; only matters when editing `.by`/`.wy` source grammars. |
| `xaw3d` / Motif / Lucid X toolkits | configure.ac toolkit selector | Already dropped per `meson.options:52-53`. |
| `gconf` | configure.ac AC_ARG_WITH | Deprecated; option `disabled` by default. |
| `imagemagick` | configure.ac AC_ARG_ENABLE | `disabled` by default; security advisories argue against turning back on. |

To revive a parked backend, start by `git show 08a22b8965ec:<path>`
and translate the rules into a new Meson `subdir()` block.  Update
`meson.build`'s parked-subdirs list and `meson.options` (which
keeps a stub list of parked option names) when promoting one.

## Compilation caching (ccache)

Both the local devenv and CI wrap the Nix-wrapped `cc`/`c++` with
ccache as a compiler launcher.  `devenv.nix` exports
`CC="ccache <nix-cc>"` (multi-word -- Meson splits on whitespace and
treats `argv[0]` as the launcher), so no `meson.build` changes are
needed.  CI uses `hendrikmuhs/ccache-action` with separate 500 MB
cache entries per matrix variant (`Linux/GTK3`, `Linux/no-X`,
`macos-14-terminal`); the action restores the cache before
`meson setup` and saves at job end.  Locally, ccache uses its
default directory (`~/.cache/ccache` on Linux,
`~/Library/Caches/ccache` on macOS).

Inspect with `ccache --show-stats`.  Bypass with
`CCACHE_DISABLE=1 meson compile -C build`.  ccache does NOT cache
`.eln` native-comp artefacts or link steps -- the `build/`
actions/cache entry handles link outputs across runs.

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
- Android: arm matrix (armeabi-v7a + arm64-v8a) defined in
  `release.yml`; until the Meson Android recipe lands the matrix
  entries emit a status doc rather than an APK.
