# Upstream backport review — 2026-05-20T1931 UTC

- Anchor: `08a22b8965ec` (; Don't skip 'vc-test-src-version-diff' test) — 2026-04-27
- Range: `08a22b8965ec..dev` vs emacs-upstream/master (258 behind)
- Reviewed: 51   Applied: 28   Retried (-X theirs): 0   Skipped: 15   Needs review: 5   Failed (conflict): 3   News-port-required: 0

## Applied

| Original SHA | New SHA | Subject | Bucket |
|---|---|---|---|
| `f68e7a0a4118` | `aab7714f0b40` | ; Improve documentation of commands that move by compilation errors | lisp-doc-style |
| `1832a93547bf` | `a8ba6bd1510b` | ; * src/fns.c (Fequal): Doc fix. | small-src+mergiraf? |
| `d89054627c4e` | `a1111b09d2ee` | Fix updates of embedded formulas by 'calc-embedded-update-formula' | lisp-bugfix |
| `cf693ce05921` | `b0e528fed28d` | Grow styled_format's frame somewhat | small-src+mergiraf? |
| `f599a9227708` | `cb75b49cfb7f` | Shrink styled_format's frame quite a bit | small-src+mergiraf? |
| `b7825c3a271e` | `c3667b639ccd` | Fix auth-source-backends-parse | lisp-bugfix |
| `0977d5915d19` | `b8bf7521ca56` | Eglot: add left-fringe code action indicator (bug#80326) | lisp-bugfix |
| `36036e71c0c2` | `b5ad10b94317` | Jsonrpc: migrate more tests to Python subprocess fixtures | test-only |
| `6c1829bf4c5a` | `066680f208b7` | Eglot: fix thinko in recent markdown-related commit (bug#81063) | lisp-bugfix |
| `7626993c6fce` | `d61afee473b0` | Remove SAFE_ALLOCA_LISP_EXTRA | small-src+mergiraf? |
| `a557bf69b49a` | `0af95f734b51` | Ensure that process-tests clean up test processes | test-only |
| `1d7d6ffedbce` | `98bd506e4246` | ; * etc/PROBLEMS: Fix entries about display of Emoji on TTY (bug#81052). | doc-only |
| `eb90c528f38a` | `cf1c26cceb96` | ; * lisp/progmodes/eglot.el (eglot-code-action-indications): Tweak. | lisp-doc-style |
| `6bd73af24136` | `d8c94d29c896` | ; * test/lisp/jsonrpc-tests.el: Adjust timeouts for CI EMBA testing | test-only |
| `10e91e096d8b` | `fe875c0b16de` | Get selected item in newsticker list view | lisp-bugfix |
| `8c71b0d6b880` | `6424e9a5ecad` | shr.el: Don't insert image at outdated destination (bug#80945) | lisp-bugfix |
| `56ae704e5b2f` | `c084a575d364` | Fix (ash -1 1) undefined behavior | small-src+mergiraf? |
| `f5c3ddd9ad3f` | `511c1cbae39b` | Prefer singed type to size_t in Fdefine_charset_internal | small-src+mergiraf? |
| `b9e20e39953a` | `6d30127d23ac` | Avoid malloc/free pairs in emit_static_object | small-src+mergiraf? |
| `7587bb2654a6` | `39445405682a` | Simplify module_extract_big_integer size calcs | small-src+mergiraf? |
| `07fe0b297bc7` | `4f471d7ee83e` | Fix undefined behavior in maybe_resize_hash_table | small-src+mergiraf? |
| `71336e837a51` | `c99f10eabb73` | Pacify GCC 16.1.1 -Wanalyzer-null-dereference | small-src+mergiraf? |
| `b3b3e203cc92` | `7ebb6f11ecd7` | Fix unlikely dump_off overflow in pdumper | small-src+mergiraf? |
| `fe33900747e4` | `ea18b5d93ddd` | Simplify serial_open | small-src+mergiraf? |
| `2dbfed05322b` | `c89ddfc82ec7` | display_tty_menu_item eassert for absurdly long item texts | small-src+mergiraf? |
| `a8b9fad89720` | `410a4631cc8d` | Make X_ERROR_MESSAGE_SIZE dependency more explicit | small-src+mergiraf? |
| `0b5ead992351` | `ffb30510bed2` | Detect some API violations in combine-change-calls (bug#80877) | lisp-bugfix |
| `3131d5660691` | `871943ad8457` | Avoid crash in doprnt | small-src+mergiraf? |

## Needs review (grouped by area)

### src/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `1fae14a022f8` | Streamline styled_format aux allocation | 35 | unclassified |
| `efb83df33142` | Don’t trust RLIMIT_NOFILE in src/process.c | 115 | unclassified |

### lisp/progmodes/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `389874c533bb` | Eglot: unbreak for treesit-less builds | 16 | lisp-no-bug |

### lisp/vc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `28a13b01c7d7` | vc-refresh-state: Override default-directory for backend functions | 14 | lisp-no-bug |

### etc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `e381cf1fc97f` | Allow child processes to continue after EPIPE | 135 | lisp+src |

## Failed (cherry-pick aborted)

| SHA | Subject | Conflict |
|---|---|---|
| `24f9e6a69362` | Make styled_format more compatible with igc | conflict:src/editfns.c |
| `d4cb550dba6c` | ; Improve last change | conflict:test/src/process-tests.el |
| `c80d22dcfcc3` | Remove stray inrange_pipe comment | conflict:src/process.c |

## Skipped

| SHA | Subject | Reason |
|---|---|---|
| `edc19c353696` | Always compile w32image.c on MinGW (Bug#80924) | autotools |
| `0179e3e062b9` | Work around GCC bug 125116 | autotools |
| `0848cbb326ca` | * admin/notes/documentation: Recommend not using "it's". | admin |
| `cbc912ed637a` | ; * admin/notes/jargon: Add entries. | admin |
| `311f1fe2ba2a` | Cut the emacs-31 release branch | autotools |
| `0d287aa2761a` | Bump master Emacs version to 32.0.50 | autotools |
| `ddde687b3f93` | ; * admin/admin.el (set-version): Fix punctuation. | admin |
| `991f6100eb1f` | ; * admin/make-tarball.txt: Suggest load-file, not require. | admin |
| `1ec79b48f380` | ; Update exported ChangeLog files and etc/AUTHORS | autotools |
| `8d0bf280a64a` | ; * ChangeLog.5: Some fixes and tidying up. | admin |
| `730d3884dc3e` | ; Fix the build broken by a typo in configure.ac | autotools |
| `5e0b4b96bc5a` | ; Adapt files in admin/notes for emacs-31 branch | admin |
| `a8f67a1f0670` | Change ERC version for Emacs 31 to 5.6.2.31.1 | release-branch |
| `c2a24dcec8ba` | ; update msys2 build helper for Emacs 31 & UCRT | admin |
| `13039e3442b8` | ; touch-up last commit: copyright and comments | admin |
