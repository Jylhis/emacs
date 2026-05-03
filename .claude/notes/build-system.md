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
