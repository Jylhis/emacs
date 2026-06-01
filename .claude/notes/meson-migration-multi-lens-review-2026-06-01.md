# Meson migration multi-lens review — 2026-06-01

Five-lens audit of the autotools → Meson+Ninja migration on the
`dev` branch.  Reviewers ran in parallel; this document
deduplicates and prioritises their findings, then cross-references
the prior audit notes so already-known items are cited rather than
restated.

## Resolution status

Findings followed up since the audit landed:

| ID    | Resolved by commit | Status |
|-------|--------------------|--------|
| F-01  | `meson: map host_machine.system() to upstream SYSTEM_TYPE` | fixed |
| F-02  | `meson: enumerate compile-main lisp at build time, not configure time` | fixed |
| F-06  | `meson: drop inert options and parked GNUstep templates` | fixed |
| F-07  | `meson: drop inert options and parked GNUstep templates` | fixed |
| F-26  | `Delete autotools-era orphaned scripts in build-aux/ and meson/` | fixed |
| F-29  | `Delete autotools-era orphaned scripts in build-aux/ and meson/` | fixed |
| F-23  | `Harden build scripts against hostile inputs (F-23, F-33, F-39)` | fixed |
| F-33  | `Harden build scripts against hostile inputs (F-23, F-33, F-39)` | fixed |
| F-39  | `Harden build scripts against hostile inputs (F-23, F-33, F-39)` | fixed |
| F-50  | `; Note phase 8 status in build-system notes (F-50)` | fixed |
| F-08  | `meson: produce a canonical EMACS_CONFIGURATION triple and define BINDIR` | fixed |
| F-22  | `meson: produce a canonical EMACS_CONFIGURATION triple and define BINDIR` | fixed |
| F-11  | `Surface failures in native-comp + sandbox install resolve (F-11, F-14)` | fixed |
| F-14  | `Surface failures in native-comp + sandbox install resolve (F-11, F-14)` | fixed |
| F-13  | `meson: plumb android-target-api through the APK pipeline (F-13)` | fixed |
| F-40  | n/a — over-flagged; the function-probe loop pattern is uniform across ~30 entries and gating one is inconsistency, not safety | rejected |

Open P0s requiring larger refactors / decisions:

- **F-03** byte-compile race on source-tree `.elc`.  Clean fix is
  per-target staging dir, but loaddefs (F-12) shares the same root
  cause and loadup.el resolves loaddefs through EMACSLOADPATH —
  multi-file refactor.
- **F-04 / F-05** CI `continue-on-error: true` flags.  Comments at
  `.github/workflows/meson.yml:440-446` say flakiness is *intentionally
  tolerated* during post-cutover recovery.  Flipping needs either a
  pbootstrap fix first or a narrow fail-if-pdmp-missing gate.

## Executive summary

**Counts after deduplication.**

|       | Security | Simplify | Correct | TDD | Parity | Total |
|-------|---------:|---------:|--------:|----:|-------:|------:|
| P0    | 0        | 2        | 4       | 2   | 0      | **7** |
| P1    | 3        | 4        | 7       | 3   | 4      | **21**|
| P2    | 4        | 5        | 6       | 4   | 6      | **22**|
| Total | 7        | 11       | 17      | 9   | 10     | **50**|

Raw lens output was 55 entries; five merged because two or more
lenses caught the same root cause.

**Top 5 P0 findings (everything that needs attention before the next
"safe to refactor" milestone).**

1. `SYSTEM_TYPE` is `"linux"`, not `"gnu/linux"` — breaks ~60 elisp
   callers that test `(eq system-type 'gnu/linux)` (battery, dired-aux,
   man, etc.). Wide functional regression that smoke tests do not
   catch. *(F-01)*
2. Byte-compile chain writes `.elc` into the **source tree** before
   moving — races on `lisp/subr.elc` between `compile-first` and
   `compile-main`, and leaves stale `.elc` behind on cancelled
   builds. *(F-03)*
3. Native-comp pdmp dump and **every** ERT/install/smoke step in
   `.github/workflows/meson.yml` is `continue-on-error: true`.
   A green CI run is no longer evidence the binary works. *(F-04,
   F-05)*
4. `compile-main` byte-compile manifest is built from a configure-
   time `_all_lisp_paths` while the manifest itself regenerates at
   build time — incremental builds miss generated loaddefs files.
   *(F-02)*
5. Three additional inert options (`silent-rules`, `autodepend`,
   `android-debug`) silently accept flags and do nothing — same
   class as the parity audit's inert list but new entries.  Also
   `Info-gnustep.plist` and `Emacs.desktop` are still generated on
   every configure for a target the fork has parked. *(F-06, F-07)*

The new local commit `27e72824b16` (mailutils probe fix) does not
intersect any finding.  Origin/dev had no new commits at audit
time; upstream/master drift since 2026-05-31 produced 7 commits,
five of which touch the doc-translations machinery (see F-19).

## Methodology

- **Stage 1** — five parallel reviewer agents
  (`jylhis-skills-core:reviewer`), one per lens: security,
  simplification, correctness, TDD coverage, autotools parity.
  Each produced a structured P0/P1/P2 report with file:line
  citations and explicit prior-art references.
- **Stage 2** — single synthesis pass (this document):
  deduplicate, prioritise, cross-reference prior notes.
- **Commit pins** (audit reproducibility):
  - `dev`: `27e72824b166a324786c5eb572d169a3221e43ce`
  - `origin/dev`: `7e61494ce6d65ac3c35bc3456a0522031052f3c6`
    (local is 1 ahead — mailutils-probe fix)
  - `upstream/master`: `75d8e5773dede1d6c429bd08a4b8d5a0d87fe87b`
- **Prior notes consulted**:
  - `build-system.md`
  - `build-system-parity-2026-05-31.md`
  - `devenv-gaps.md`
  - `library-replacement-audit.md`
  - `developer-tools.md`

Each finding cites prior art when applicable; "new" means no
existing note covers it.  P-01 explicitly *contradicts* a bullet in
the parity audit and recommends retracting it.

## Findings

### P0 — must fix before next refactor

#### F-01 — `SYSTEM_TYPE` emits wrong Lisp symbol on Linux
- Lens(es): correctness
- Files: `meson.build:45`, `src/emacs.c:3076-3086`
- Prior art: new
- What's wrong: `conf_data.set('SYSTEM_TYPE', host_machine.system())`
  writes `"linux"` / `"darwin"` / `"android"` verbatim into
  `config.h`; `emacs.c` interns it into `Vsystem_type`.  Upstream
  emits `gnu/linux` for `*-gnu-linux*` opsys.  Every Lisp test
  like `(eq system-type 'gnu/linux)` now returns nil
  (battery.el:100/104/107, dired-aux.el:1439, man.el:914, and
  ~60 others).
- Upstream autotools equivalent: `configure.ac:1058-1090` opsys
  case + `AC_DEFINE_UNQUOTED(SYSTEM_TYPE, "$opsys")`.
- Fix shape: map `host_machine.system()` → upstream opsys symbol
  before `set()`.

#### F-02 — Non-deterministic byte-compile manifest in `compile-main`
- Lens(es): correctness
- Files: `lisp/meson.build:107-118`, `meson/byte_compile_batch.py:82-84`
- Prior art: new
- What's wrong: `_all_lisp_paths` is captured at configure time but
  the manifest regenerates at build time, after loaddefs run.
  New loaddefs files end up *included* by the manifest yet not
  declared as deps; deletions don't invalidate. Stale incremental
  rebuilds become silently wrong.
- Fix shape: drop the configure-time glob; depend on
  `loaddefs_stamp` and treat manifest output as the truth.

#### F-03 — `byte_compile_batch.py` writes `.elc` into the source tree
- Lens(es): correctness
- Files: `meson/byte_compile_batch.py:163-180`,
  `meson/byte_compile.py:80-86`, `meson/run_loaddefs.py:65-69`,
  `meson/run_leim.py`
- Prior art: new (parity audit only mentioned the analogous
  source-tree write for `charscript`)
- What's wrong: `batch-byte-compile` emits `*.elc` next to the
  source `.el`; the script then `shutil.move`s into `build/lisp/`.
  Concurrent `meson compile -j` runs of `compile-first` and
  `compile-main` overlap on `lisp/subr.elc`, `lisp/keymap.elc`,
  etc. — race on the same write.  A cancelled build leaves stray
  `.elc` shadowing future compiles via `load-prefer-newer`.
  `run_loaddefs.py:65-72` unlinks source-tree loaddefs before
  generation (see also F-12).
- Fix shape: byte-compile from a per-target staging copy
  (symlink/copy `.el` into a build subdir); never write into
  `lisp/`.

#### F-04 — Native-comp pdmp dump is `continue-on-error: true`
- Lens(es): tdd
- Files: `.github/workflows/meson.yml:447, :451, :455, :461, :465`
- Prior art: new
- What's wrong: Five sequential build steps
  (`bootstrap-emacs.pdmp`, `compile-first`, `loaddefs-stamp`,
  `compile-main`, `emacs.pdmp`) all swallow failure.  The
  `required` gate at `:748` doesn't see them — a regression in
  any of `run_dump.py`/`run_loaddefs.py`/`byte_compile_batch.py`
  produces a green CI with no pdmp, and every downstream test
  silently skips with "missing pdmp".
- Missing test: a hard `test -f build/lisp/emacs.pdmp || exit 1`
  step on the GTK3 matrix.
- Fix shape: split per-matrix-row continue-on-error gates instead
  of blanket `true`.

#### F-05 — Every ERT/install/smoke step in CI is advisory
- Lens(es): tdd
- Files: `.github/workflows/meson.yml:482, :505, :514, :528,
  :538, :549, :565`
- Prior art: new
- What's wrong: Smoke factorial, `meson test --suite smoke`, full
  ERT, staged install, `check-install-parity.sh`, installed-batch
  eval, avy reproducer — all `continue-on-error: true`. Only
  `temacs`/`bootstrap-emacs`/`etc/DOC` compile and lib-src
  binaries actually gate the matrix.  CI cannot detect any
  post-link regression.
- Missing test: on `Linux/GTK3`, ERT smoke + parity check are
  mandatory; only `Linux/no-X` stays advisory.
- Fix shape: key `continue-on-error` off `matrix.label ==
  'Linux/no-X'`.

#### F-06 — Three inert options (`silent-rules`, `autodepend`, `android-debug`)
- Lens(es): simplify
- Files: `meson.options:234, :197, :244`
- Prior art: `build-system-parity-2026-05-31.md` §3 mentions
  `silent-rules` as `n/a-cosmetic` and `autodepend` as
  `missing-cosmetic`; `android-debug` is **new**.  All three are
  declared options that accept user values and produce no effect.
- What's wrong: `meson configure -Dautodepend=disabled` or
  `-Dandroid-debug=false` returns success and changes nothing.
  Misleads users about what's tunable.
- Fix shape: delete the three options; add a one-line comment
  pointing at Ninja's native behaviour.

#### F-07 — `Info-gnustep.plist` and `Emacs.desktop` generated for a parked target
- Lens(es): simplify + correctness + parity (three lenses)
- Files: `nextstep/meson.build:33-42`,
  `nextstep/templates/Info-gnustep.plist.in`,
  `nextstep/templates/Emacs.desktop.in`
- Prior art: `build-system-parity-2026-05-31.md` §8/§10 (GNUstep
  parked; the X11 desktop entry is `etc/emacs.desktop`).
- What's wrong: Both `configure_file()` calls render output that no
  consumer reads (neither `run_app_bundle.py` nor the install
  script copies them).  Creates stale artefacts under
  `build/nextstep/`; misleads readers about GNUstep support.
- Fix shape: delete the two `configure_file()` calls and the two
  templates.

### P1 — latent or partial

#### F-08 — `EMACS_CONFIGURATION` canonical triple malformed
- Lens(es): correctness
- Files: `meson.build:40-41`
- Prior art: new
- Detail: `cpu_family() + '-pc-' + system()` yields
  `x86_64-pc-linux` on Linux (autotools: `x86_64-pc-linux-gnu`)
  and `aarch64-pc-darwin` on macOS (autotools:
  `aarch64-apple-darwin23`).  User-visible via `(emacs-version t)`,
  `system-configuration`, downstream packaging.
- Fix shape: pick the vendor/abi suffix per OS.

#### F-09 — `run_charsets.py` writes outside `@OUTDIR@` into source tree
- Lens(es): correctness
- Files: `meson/run_charsets.py:313, :335-344`,
  `admin/meson.build:23-24`
- Prior art: new (parity audit only flagged install gap for
  `build/etc/charsets/`)
- Detail: `--out-dir` points to `$SRC/etc/charsets/`,
  `--lispint-dir` to `$SRC/lisp/international/`.  Also writes
  `out_dir.parent / ".jisx2131-filter"` (stale dotfile in source
  tree, never cleaned).  Read-only source mount breaks; clean
  builds aren't reproducible.
- Fix shape: redirect outputs into the build tree; let
  `meson_install.py` copy.

#### F-10 — Subprocess errors silently swallowed across scripts
- Lens(es): correctness
- Files: `meson/run_charsets.py:164,246,263,269,279,295,323,329,
  337,341,343`, `meson/run_leim.py:181-196`
- Prior art: new
- Detail: `subprocess.run(["awk", ...], capture_output=True).stdout`
  reads `.stdout` but ignores `returncode`/`stderr`.  If awk/sed/
  gunzip fails (e.g. missing GB18030.gz), an empty map is written
  silently and the stamp marks success.  Subsequent unidata/loaddefs
  builds then read garbage.
- Fix shape: `check=True` consistently, or capture rc+stderr and
  `sys.exit(rc)`.

#### F-11 — `native_compile.py` silent success on chunk failures
- Lens(es): correctness
- Files: `meson/native_compile.py:73-84`
- Prior art: new
- Detail: failing chunks increment `failed` but the stamp is
  written and the script returns 0.  Meson sees native compilation
  as done even when every chunk crashed; stale empty `native-lisp/`
  cache persists across rebuilds.
- Fix shape: non-zero exit when any chunk fails; record failing
  chunks in stamp content.

#### F-12 — `loaddefs_stamp` unlinks source-tree files before generation
- Lens(es): correctness
- Files: `meson/run_loaddefs.py:65-72`, `lisp/meson.build:131-137`
- Prior art: new (related to F-03)
- Detail: every `*-loaddefs.el` and `loaddefs.el` under `lisp/` is
  unconditionally unlinked before bootstrap-emacs runs.  If
  bootstrap-emacs crashes (which `byte_compile_batch.py` comments
  acknowledge happens), the source tree is left with no loaddefs.
  Next configure's `list_lisp_files` returns a manifest missing
  those files; they're never regenerated until `loaddefs.stamp` is
  manually deleted.
- Fix shape: stage writes in a build dir; `cp` into `lisp/` only
  on success.

#### F-13 — `build_android_apk.py` hard-codes `target_api = 35`
- Lens(es): correctness
- Files: `meson/build_android_apk.py:38-54, :222`
- Prior art: new
- Detail: ignores `--api` (min_api).  `find_jar` falls back to
  highest available SDK silently; APK ships with wrong
  `--target-sdk-version`.
- Fix shape: pass target_api through CLI; hard-error if
  `android-N.jar` is missing under a `--strict` mode.

#### F-14 — `meson_install.py` resolve() lacks DESTDIR-escape check
- Lens(es): correctness + security
- Files: `meson/meson_install.py:107-115`
- Prior art: new
- Detail: `resolve(p)` does `path.relative_to(install_prefix)` then
  joins to `destdir_prefix`, but doesn't reject absolute paths that
  escape the prefix (e.g. `--mandir=/etc/cron.d`).  Under sudo
  install or a DESTDIR with prepared symlinks, writes outside
  DESTDIR.
- Fix shape: after joining, assert the resolved path is inside
  `destdir_prefix` (`realpath -e` or `Path.resolve()` then
  `is_relative_to`).

#### F-15 — NS bundle ships without Info pages when makeinfo missing
- Lens(es): correctness
- Files: `nextstep/meson.build:77`, `meson.build:1101-1106`,
  `meson/run_app_bundle.py:91`
- Prior art: new
- Detail: `--info-dir` is `build/doc/`, but `doc/` is only `subdir`'d
  when `not want_android`.  `run_app_bundle.py:91` skips info copy
  silently when the directory is empty — bundle ships without Info,
  no error.
- Fix shape: require `makeinfo` when `-Dns-self-contained=enabled`,
  or fail loudly when info-dir is empty.

#### F-16 — `check-install-parity.sh` is presence-only
- Lens(es): tdd
- Files: `.github/scripts/check-install-parity.sh:28-49, :60-66`
- Prior art: `build-system-parity-2026-05-31.md` §1 (option
  inventory only)
- Detail: tests `-e`; an empty file, broken symlink, or
  non-executable `bin/emacs` passes.  No `--version` check, no
  `info/dir` verification, no `.elc` load smoke.  The workflow's
  step `:548` *does* eval, but `continue-on-error: true` (see F-05).
- Missing test: `"$bindir/emacs" --batch --eval '(kill-emacs 0)'`
  exits 0; `(require 'dired)` exits 0; `info/dir` contains an Emacs
  entry.
- Fix shape: add an executable/runtime tier between presence checks
  and elc count.

#### F-17 — CI feature-flag matrix exercises only GTK3 + no-X + macOS-terminal
- Lens(es): tdd
- Files: `.github/workflows/meson.yml:234-253, :654-686`
- Prior art: `build-system-parity-2026-05-31.md` (option inventory)
- Detail: out of ~35 upstream knobs, CI runs two Linux variants and
  one macOS-terminal variant.  Untested: `-Dnative-compilation=yes`
  on Linux, `-Dmodules=disabled`, `-Dthreads=disabled`,
  `-Dpgtk=enabled`, `-Dns=enabled` (Cocoa GUI), Android cross.
  Downstream packagers (`homebrew-emacs-plus`, `nix-darwin-emacs`,
  `MacPorts` — tracked under `.claude/notes/fork-*.md`) build these
  routinely.
- Missing test: matrix rows for `{native-comp:yes,no} ×
  {modules:disabled} × {threads:disabled}` on Linux/GTK3 and
  `-Dns=enabled` on macOS.
- Fix shape: expand `strategy.matrix.include`.

#### F-18 — Native-comp never exercised in CI
- Lens(es): tdd
- Files: `.github/workflows/meson.yml:667`; absence in `:240-253`
- Prior art: new
- Detail: macOS forces `-Dnative-compilation=no`; Linux leaves it
  at default (off in current options).  No row exercises the
  `meson/native_compile.py` path, `.eln` install layout, or
  `eln-cache` runtime resolution.  CLAUDE.md *recommends*
  `-Dnative-compilation=yes` as the dev build — CI never proves it
  works.
- Missing test: Linux/GTK3+nativecomp matrix row that builds,
  installs, runs `(native-compile "lisp/subr.el")`, loads the
  `.eln`.
- Fix shape: add the row; keep `meson test` mandatory.

#### F-19 — `doc/translations/` diverged on upstream (May 30 – Jun 1)
- Lens(es): parity
- Files: `doc/meson.build:196-230`, `doc/translations/` (only
  `fr/misc/ses-fr.texi` present)
- Upstream autotools equivalent: upstream `Makefile.in:118`
  (`DOCLANGS?=@DOCLANGS@`), `:1149-1162` (`MAKE_DOC_FOR_DOCLANG`);
  `doc/misc/Makefile.in:66-81`.
- Prior art: new (commits `c44f7ada0c0`, `35af8d1099e`,
  `3d01d53c1e3`, `8902361cba8`, `75d8e5773de` after 2026-05-30).
- Detail: upstream now drives info/dvi/html/pdf/ps per language via
  `$(DOCLANGS)` and errors on unknown languages.  Meson hardcodes
  one tuple `['fr', 'misc', 'ses-fr']` with no error/skip logic and
  no language-list option — new translation trees are silently
  ignored.
- Fix shape: enumerate `doc/translations/*/`; error on missing
  `info_common.mk`; accept `-Ddoc-languages=`.

#### F-20 — `admin/unidata` partial regeneration (5 outputs absent from Meson DAG)
- Lens(es): parity
- Files: `meson/run_unidata.py:64-135`, `admin/meson.build` (no
  entries for the missing outputs)
- Upstream autotools equivalent: `admin/unidata/Makefile.in:46-49`
  declares `${top_srcdir}/src/macuvs.h`, `emoji-labels.el`,
  `uni-scripts.el`, `uni-confusable.el`, `idna-mapping.el` as
  build outputs.
- Prior art: new (parity audit only covered `uni-*.el` and
  `charprop.el`)
- Detail: `run_unidata.py` regenerates only `uni-*.el` and
  `charprop.el`.  Four `.el` outputs are absent from the working
  tree (verify with `ls lisp/international/emoji-labels.el`); on
  a clean checkout the bundled lisp tree is incomplete vs upstream.
  A bump to `UnicodeData.txt`, `emoji-data.txt`, `confusables.txt`,
  `IdnaMappingTable.txt`, or `IVD_Sequences.txt` silently won't
  propagate.
- Fix shape: extend `run_unidata.py` to invoke `unidata-gen-emoji-
  labels`, `unidata-gen-scripts`, `unidata-gen-confusable`,
  `unidata-gen-idna-mapping`, and `uvs-print-table-ivd`.  Add to
  `unidata_stamp` deps in `src/meson.build:512`.

#### F-21 — `-Dchecking=` array still silent no-op (UNFIXED)
- Lens(es): parity + simplify
- Files: `meson.options:181-187`, `meson/config.h.in` (absent
  `ENABLE_CHECKING`, `GLYPH_DEBUG`, `GC_CHECK_*`, `XASSERTS`,
  `CHECK_STRUCTS`)
- Upstream autotools equivalent: `configure.ac:703-786`,
  `AC_SUBST([CHECK_STRUCTS])` at :764
- Prior art: `build-system-parity-2026-05-31.md` §10 #5 — **still
  unfixed at HEAD**.  CLAUDE.md instructs developers to use
  `-Dcheck=yes,glyphs` for debug builds; this currently produces
  a non-debug binary.
- Fix shape: parse the array option into matching `conf_data.set()`
  calls.

#### F-22 — `BINDIR` macro still missing (now correlates with `pdumper.c:5557`)
- Lens(es): parity + correctness
- Files: `meson/config.h.in` (absent), `meson.build` (absent),
  `src/pdumper.c:5551-5559`
- Upstream autotools equivalent: `configure.ac:7172`
- Prior art: `build-system-parity-2026-05-31.md` §4 + §10 #16 —
  still unfixed; new evidence (pdumper code path) raises priority.
- Detail: `src/pdumper.c:5557-5558` uses `BINDIR` unconditionally
  inside `#if HAVE_NS && !NS_SELF_CONTAINED`.  With Meson defining
  neither macro the compiler sees a literal `BINDIR` identifier —
  resolution depends on whatever gnulib leaves around.
- Fix shape: `conf_data.set_quoted('BINDIR', bindir + '/')`
  alongside the install_dir resolution.

#### F-23 — `admin/download-android-deps.sh` unquoted positional args
- Lens(es): security
- Files: `admin/download-android-deps.sh:14, 20, 25-26, 32`
- Prior art: new
- Detail: `mirror=${2-…}` and `curl -OL $mirror/$1` are unquoted.
  A whitespace-bearing mirror smuggles curl flags (`--config /etc/
  passwd`, `--upload-file`, `-K`).  Hash pinning catches a tampered
  tarball **after** curl runs.  Bash-only `[ "$1" == "64" ]` under
  `#!/bin/sh` means the script never ran under dash (functional bug
  too).
- Fix shape: quote every expansion; `curl --proto =https --tlsv1.2
  -fsSLo "$1" -- "$mirror/$1"`; allowlist the mirror.

#### F-24 — `actionlint` installer piped from `curl | bash` against `main`-branch URL
- Lens(es): security
- Files: `.github/workflows/meson.yml:219`
- Prior art: new
- Detail: `bash <(curl -s https://raw.githubusercontent.com/rhysd/
  actionlint/main/scripts/download-actionlint.bash)` resolves
  against `main` every CI run.  A compromised maintainer account
  executes arbitrary code in the lint job.  No `-f` on curl —
  5xx is silently piped as an empty script.
- Fix shape: pin the installer URL to a tagged SHA; hash-verify
  the resulting binary, or `nix run nixpkgs#actionlint` from
  devenv.

#### F-25 — `setup-devenv` action evals untrusted env values via `BASH_ENV`
- Lens(es): security
- Files: `.github/actions/setup-devenv/action.yml:54-95`
- Prior art: new
- Detail: captures `declare -px` from `devenv shell`, filters by
  *name* only, writes to `/tmp/devenv-env.sh`, loads via
  `BASH_ENV`.  A devenv-pinned nixpkgs package setting a hostile
  var (`BASH_FUNC_cc%%=() { … }` or values containing `$(…)`) is
  sourced wholesale.  `/tmp/` is multi-tenant-predictable on
  self-hosted runners.
- Fix shape: allowlist env-var names rather than blacklist; use
  `$RUNNER_TEMP`; validate values match a safe regex.

#### F-26 — `meson/byte_compile.py` is orphaned
- Lens(es): simplify
- Files: `meson/byte_compile.py:1-91`
- Prior art: new
- Detail: 90-line single-file byte-compiler not referenced by any
  `meson.build`.  Only `byte_compile_batch.py` is wired in.  Other
  references are doc comments.
- Fix shape: delete.

#### F-27 — Six scripts reimplement EMACSDATA/EMACSDOC/EMACSLOADPATH setup
- Lens(es): simplify
- Files: `meson/byte_compile_batch.py:22-33,86-89`,
  `meson/run_dump.py:82-85`, `meson/run_loaddefs.py:74-84`,
  `meson/run_leim.py:39-50`, `meson/run_org_to_texi.py:53-63`,
  `meson/run_test.py:34-61`, `meson/run_unidata.py:88-101`,
  `meson/byte_compile.py:63-66`
- Prior art: new
- Detail: each script independently builds
  `EMACSLOADPATH = ":".join(lisp + lisp-subdirs)` and
  `EMACSDATA`/`EMACSDOC`.  Three different enumeration strategies
  coexist.  `intl/charscript.el + emoji-zwj.el` staging block
  copy-pasted across four scripts.
- Fix shape: `meson/_emacs_env.py` with `make_env(src_root)` and
  `stage_intl(...)`; ~100 LOC saved.

#### F-28 — `compile_first_manifest` abuses `configure_file()` with `sh -c` heredoc
- Lens(es): simplify + correctness
- Files: `lisp/meson.build:63-77`
- Prior art: new
- Detail: a static 9-line manifest is rendered by
  `configure_file(command : ['sh', '-c', 'cat > $1 <<EOF\n…\nEOF',
  …])`.  Depends on `sh` having literal newline handling for the
  heredoc; Meson's command escaping varies by Ninja/OS/shell.
  Could be a checked-in `compile-first.manifest` consumed via
  `files()`.
- Fix shape: check in the static file; use `files()`; delete the
  custom_target.

#### F-29 — Seven orphaned files in `build-aux/` from the autotools era
- Lens(es): simplify
- Files: `build-aux/makecounter.sh:1-44`, `build-aux/dir_top`,
  `build-aux/ndk-build-helper{,-1,-2,-3,-4}.mk`,
  `build-aux/ndk-module-extract.awk`, `build-aux/make-info-dir`
- Prior art: new
- Detail: `makecounter.sh` produced `lisp.mk`'s counter under
  autotools (never invoked from Meson); `ndk-build-helper-*.mk`
  and `ndk-module-extract.awk` were the autotools Android NDK glue
  (parity audit §10 marks `subdir('cross/ndk-build')` parked, and
  the new pipeline uses `build_android_apk.py`); `make-info-dir`
  replaced by `install-info` in `meson_install.py`; `dir_top`
  referenced only by `makecounter.sh`.
- Fix shape: delete the seven files.  Keep `gitlog-to-changelog`,
  `gitlog-to-emacslog`, `update-copyright`, `update-subdirs`.

### P2 — hygiene & cleanup

#### F-30 — Hard-coded APK signing credentials with default `emacs1`
- Lens(es): security + correctness
- Files: `meson/build_android_apk.py:180-191`
- Prior art: new
- Detail: passes passphrases on the command line
  (`--ks-pass pass:…`), visible in `/proc/*/cmdline`.  A downstream
  packager exporting a real `EMACS_APK_STOREPASS` leaks it.
- Fix shape: `pass:env:VAR` / `pass:file:PATH` forms.

#### F-31 — `process_in_h.py --set` lets values inject preprocessor directives
- Lens(es): security
- Files: `meson/process_in_h.py:27-34, :89-94`
- Prior art: new
- Detail: override values via `--set NAME=VALUE` or `--json` are
  written verbatim into gnulib `*.in.h` outputs.  A value
  containing newline + `#include "/etc/shadow"` lands in a
  generated header.  Defense-in-depth: today's callers are all
  meson-controlled.
- Fix shape: reject override values containing newlines or `*/`;
  document the contract.

#### F-32 — `meson_install.py` resolves `install-info`/`glib-compile-schemas` from PATH
- Lens(es): security
- Files: `meson/meson_install.py:299-336`
- Prior art: new
- Detail: `shutil.which("install-info")` resolves through inherited
  PATH; `sudo -E meson install` executes whatever binary appears
  first.
- Fix shape: locate from a fixed PREFIX, or fail loudly when
  elevated and PATH is non-system.

#### F-33 — `update-subdirs` doesn't escape directory names in generated Elisp
- Lens(es): security
- Files: `build-aux/update-subdirs:24-46`
- Prior art: new
- Detail: shell `for file in *` interpolates names into
  `subdirs.el` unescaped.  Subdir named `foo"); (delete-file …)`
  produces Elisp that runs on load.
- Fix shape: escape `"` and `\`, or rewrite as a Python helper.

#### F-34 — Three lister scripts could fold into one
- Lens(es): simplify
- Files: `meson/list_lisp_files.py` (65), `list_test_files.py`
  (35), `list_icons.py` (56)
- Prior art: new
- Fix shape: `enumerate.py --mode {lisp,tests,icons}`; ~60 LOC
  saved.

#### F-35 — `make_buildobj_h.py` could be `configure_file()`
- Lens(es): simplify
- Files: `meson/make_buildobj_h.py:1-25`, `src/meson.build:270-274`
- Prior art: new
- Fix shape: drop the script; use `configure_file(configuration :
  …)` with the existing `base_obj_basenames`.

#### F-36 — `bootstrap-emacs`/`emacs` targets are `cp` of a binary
- Lens(es): simplify
- Files: `src/meson.build:473-479, :540-546`
- Prior art: new
- Detail: two near-identical `custom_target` calls exist to give
  the dumper a distinct argv[0].  A symlink or single target with
  two outputs suffices.
- Fix shape: collapse to one target, or set `argv[0]` via wrapper.

#### F-37 — Five `leim/` `custom_target`s serially re-spawn the same Python wrapper
- Lens(es): simplify
- Files: `leim/meson.build:29-108`
- Prior art: new
- Detail: tit/misc/pinyin/ja-dic stamps each pay ~3s bootstrap-
  emacs warm-up serially; no inter-dependency between them.
- Fix shape: `run_leim.py --tit --misc --pinyin --skk-dic` emitting
  a single combined stamp.

#### F-38 — Subprocess boilerplate / signal-decode missing in 11 sites
- Lens(es): correctness + simplify
- Files: `meson/byte_compile.py:76`, `byte_compile_batch.py:128,
  147,153`, `native_compile.py:76`, `run_dump.py:118-136`,
  `run_leim.py:53-55,115,135,146,159,174`, `run_loaddefs.py:110`,
  `run_org_to_texi.py:81`, `run_test.py:75`, `run_unidata.py:122,
  133`
- Prior art: new (related to F-10 and F-11)
- Detail: only `run_dump.py:126-136` decodes a signal exit.  The
  rest discard signal info — segfaults look like ordinary non-zero
  exits, and negative rc bouncing through `sys.exit()` is taken
  modulo 256.
- Fix shape: 15-line `_emacs_env.run(cmd, env, cwd) -> int` helper.

#### F-39 — `run_charsets.py` leaks file handles
- Lens(es): correctness
- Files: `meson/run_charsets.py:265, :338-339`
- Prior art: new
- Detail: `stdin=(out_dir / "GB180302.map").open("r")` leaves the
  handle open until GC.  Breaks on Windows.
- Fix shape: `with` blocks.

#### F-40 — `HAVE_GNU_GET_LIBC_VERSION` probed on all hosts
- Lens(es): correctness
- Files: `meson.build:226`
- Prior art: new
- Detail: defensive only — but a weak-symbol shim could mis-set the
  macro.
- Fix shape: gate under `is_linux`.

#### F-41 — `make-docfile` drops `SOME_MACHINE_OBJECTS` stable-ordering prefix
- Lens(es): parity
- Files: `src/meson.build:148-170`
- Upstream autotools equivalent: `src/Makefile.in:477, :657-667`
- Prior art: new
- Detail: upstream prepends a per-platform object list so `etc/
  DOC` symbol order is stable across configurations.  Fork has
  dropped MS-DOS/Windows so the list is currently empty — fine
  today but the principle (stable string-pool ordering) is gone.
- Fix shape: document intent; preserve the prepend slot for
  future per-platform `.o` additions.

#### F-42 — `meson_install.py` info/gzip pass doesn't recurse into `infodir/<lang>/`
- Lens(es): parity
- Files: `meson/meson_install.py:296-315, :358-371`
- Upstream autotools equivalent: upstream `Makefile.in:733-754`
  iterates `$(infodir)/*.info` including subdirs.
- Prior art: new (drift created by F-19)
- Detail: `iterdir()` on `info_dst` only; per-language `.info`
  files are installed but never gzipped nor registered in `dir`.
- Fix shape: `rglob('*.info')`; pass per-dir `--info-dir`.

#### F-43 — Smoke set is three hardcoded files; no `src/` or loader smoke
- Lens(es): tdd
- Files: `test/meson.build:57-61`
- Prior art: new
- Fix shape: add `(require 'dired)` loader smoke; keep timeout
  ≤30s.

#### F-44 — No regression fixture for `process_in_h.py`/`make_*`
- Lens(es): tdd
- Files: `meson/process_in_h.py`, `meson/make_buildobj_h.py`,
  `meson/make_emacs_module_h.py` (no companion tests)
- Prior art: new
- Fix shape: `meson/tests/process_in_h_test.py` with a fixture +
  golden; register via `meson test()`.

#### F-45 — Test discovery is configure-time, no staleness check
- Lens(es): tdd
- Files: `test/meson.build:33-38`
- Prior art: new
- Detail: a developer adding `*-tests.el` and running `meson test`
  without re-`setup` won't see it.  CI happens to re-setup; humans
  don't.
- Fix shape: a `manifest-stale` test that diffs current
  enumeration against the saved manifest.

#### F-46 — No determinism test for generated headers
- Lens(es): tdd
- Files: `src/meson.build:137-181, :197-209, :255-260, :270-275`,
  `lib/meson.build:359-389`
- Prior art: new
- Fix shape: per-generator `meson test()` that re-runs and `cmp`s
  to a known-good output.

#### F-47 — `etc/charsets` install gap was a false alarm — retract from prior audit
- Lens(es): parity
- Files: `admin/meson.build:23`, `meson/run_charsets.py:118-131`,
  `meson/meson_install.py:193-215`
- Upstream autotools equivalent: `admin/charsets/Makefile.in:32`
- Prior art: `build-system-parity-2026-05-31.md` §6 "Install gaps"
  bullet 1 — **contradict and retract**.
- Detail: `run_charsets.py` writes to `meson.global_source_root() /
  'etc/charsets'`, so the source-tree install walk does pick up
  regenerated maps.  The prior bullet should be removed.
- Fix shape: edit the prior note.

#### F-48 — `emacsclient` SO_RCVTIMEO fix not yet picked
- Lens(es): parity
- Files: `lib-src/emacsclient.c`
- Upstream change: `6db4271ee8b` (Bug#81160)
- Prior art: new
- Fix shape: cherry-pick via the upstream-commit-review skill.

#### F-49 — `nextstep/meson.build` Info-gnustep `configure_file` succeeds even when template fields missing
- Lens(es): correctness
- Files: `nextstep/meson.build:33-37`
- Prior art: new (subsumed by F-07; kept as P2 detail since the
  failure mode differs slightly).
- Detail: the Info-gnustep.plist.in template can list `@vars@` not
  present in `ns_plist_data` — `configure_file` substitutes them as
  empty without erroring.
- Fix shape: drop the whole `configure_file` call (see F-07).

#### F-50 — Phases 8 & 9 unaccounted in commit log
- Lens(es): parity (documentation drift)
- Files: `CLAUDE.md` (Build section), commit `2bf867f8398`
  (Phase 9), no commit titled "phase 8".
- Prior art: new
- Detail: `git log --oneline | grep -oE "phase [0-9]+" | sort -u`
  yields `1 2 3 4 5 6 7 9 10`.  Phase 8 either rolled silently
  into other work or was skipped.  Phase numbering no longer
  self-documents.
- Fix shape: add a "phase 8 retroactive notes" paragraph to
  `build-system.md`, or rename phase 9 to phase 8 if the latter
  was a typo.

## Cross-lens deduplication map

These Stage-1 entries collapsed into single synthesis findings:

- `B-03` + `C-11` + `P-09` → **F-07** (Info-gnustep / Emacs.desktop
  parked-target render).  Three lenses caught the same root cause.
- `B-04` + `C-17` → **F-28** (compile_first_manifest heredoc).
- `S-04` + `C-13` → **F-30** (apksigner credentials in argv).
- `C-06`/`C-07`/`C-09` + `B-11` → split: **F-10** (silent awk/sed),
  **F-11** (native-comp silent success), **F-38** (signal-decode
  missing) — three distinct root causes within the same family.
- `T-04` + `T-05` → split: **F-17** (matrix breadth), **F-18**
  (native-comp specifically) — same lens, different gaps.

## Open questions for follow-up

1. **F-01 fallout.**  How many tests have been silently passing
   without exercising the `gnu/linux` branch?  A grep across
   `test/lisp/**/*-tests.el` for `system-type` would estimate.
2. **F-04/F-05 history.**  Why were the CI gates flipped to
   `continue-on-error`?  Was it a temporary measure during a flaky
   period (Phase 7 dump path)?  If so, what's the unblock
   criterion?
3. **F-20 scope.**  The four missing `lisp/international/*.el`
   files — are they intentionally absent on this fork (perhaps
   regenerated locally and not committed) or genuinely missing
   from the source tree?  `git log lisp/international/` clarifies.
4. **Phase 8 (F-50).**  Was it the autotools-removal pre-staging,
   or the NS-bundle assembly?  The user has the authoritative
   answer.
5. **F-22 cross-platform.**  Does `BINDIR` being undefined produce
   a compile failure on macOS today, or is it silently masked by
   `conf_post.h` defaulting it?  A test build with
   `-Dns=enabled -Dns-self-contained=disabled` would confirm.
6. **F-47 retraction.**  Confirm by running an actual install
   under `--destdir` and `diff -r` the source-tree vs build-tree
   `etc/charsets/` outputs.

## Reproducing this audit

- Re-run any Stage-1 agent with the prompt in
  `/home/markus/.claude/plans/jylhis-skills-core-tdd-simplify-securit-foamy-ripple.md`.
- Pin to the commit hashes in the Methodology section above.
- Findings should reproduce within ~3 finding-IDs (i.e. agents
  may number differently, but the same defects surface).
