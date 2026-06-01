# Upstream backport review — 2026-05-31T1455 UTC

- Anchor: `08a22b8965ec` (; Don't skip 'vc-test-src-version-diff' test) — 2026-04-27
- Range: `08a22b8965ec..dev` vs emacs-upstream/master (400 behind)
- Reviewed: 158   Applied: 59   Retried (-X theirs): 0   Skipped: 31   Needs review: 64   Failed (conflict): 4   News-port-required: 0

## Applied

| Original SHA | New SHA | Subject | Bucket |
|---|---|---|---|
| `9ba65aa96568` | `531ea067308f` | Fix missing margin face on display prop in erc-stamp | lisp-bugfix |
| `8095fbef7720` | `7933614aa85f` | doc/lispref/text.texi: Add complement to commit f4a1c006569f | doc-only |
| `520c5b7c71b3` | `41b40dff9854` | ; * doc/lispref/text.texi (Special Properties): Fix last change. | doc-only |
| `e90cafc2886d` | `1a6eac8a1513` | ; * doc/lispref/display.texi (Displaying Faces): Mention 'margin' face. | doc-only |
| `7d84e69a3493` | `66b3d47b766d` | hideshow: Menu entry for 'hs-toggle-all' | lisp-bugfix |
| `997fc2cef771` | `81fd1909a387` | Allow markdown-ts--run-command-in-code-block to ignore output (bug#81041) | lisp-bugfix |
| `e0aeee2dc5fc` | `dc19ea6f06bb` | Fix markdown-ts-mode atx_heading face computation (bug#81042) | lisp-bugfix |
| `aad170d1edf7` | `852f80d998bc` | markdown-ts-mode: hide fence lines in view-mode (bug#81081) | lisp-bugfix |
| `655302cc2122` | `53d1b7fa6708` | Fix 'shr-outline-search' (bug#81073) | lisp-bugfix |
| `13b29eebc166` | `d4a32274ce06` | Eglot: use standard face for completion annotations (bug#81088) | lisp-bugfix |
| `98348a0bdc97` | `540f23789b7f` | [Xt] Fix child frame resizing glitch | small-src+mergiraf? |
| `2936b36164de` | `854272595e3d` | Fix "assertion 'GTK_IS_WINDOW (window)' failed" | small-src+mergiraf? |
| `3de7f0ce5e5f` | `3721d6dacb1c` | Fix warning message in 'markdown-ts-mode--initialize' | lisp-bugfix |
| `d6f7b2d99bdb` | `f9b17a015993` | Save/restore old_buffer slot via window configurations (Bug#81097) | small-src+mergiraf? |
| `f6281d757d35` | `935beb57c348` | ; * etc/NEWS: Tell how to disable 'markdown-ts-mode'. | doc-only |
| `646702f70b38` | `d433d58f5fd4` | let-alist.el: Use 'elt' instead of 'nth' | lisp-bugfix |
| `70b79b3ed8d0` | `97952b5fd368` | Rename `icalendar-recur' type and related functions | lisp-bugfix |
| `f13287fde0d0` | `e89eed452d4c` | Revert "sh-script: Mark + and * as punctuation rather than a symbol constituent" | lisp-bugfix |
| `7a17f97baa7d` | `e4b91896df6e` | Prettify special glyphs | lisp+news-bug |
| `dd42133315b9` | `86ef88198b5c` | vc-test--rename-file: Disable part of test for SCCS | test-only |
| `1800350b1868` | `28b4a87d8d40` | Avoid compilation-mode matching rust as gnu | lisp-bugfix |
| `12eec781ed69` | `cf68fecbf0b8` | No longer raise error on HTTP 402 (Payment Required) (bug#81101) | lisp-bugfix |
| `9851c5ea3410` | `d2cfeeeefc16` | Shrink STRING_BYTES_MAX slightly | small-src+mergiraf? |
| `5fd1e0bbef85` | `2f1fcae509b9` | Coalesce load_seccomp comparisons | small-src+mergiraf? |
| `b1d338d89ae1` | `c887273003a8` | Fix misleading x_dnd_begin_drag_and_drop API | small-src+mergiraf? |
| `8c69ba718e85` | `fc2c493771d5` | Fix emit_static_object comment (no bzero call) | small-src+mergiraf? |
| `42a8e12088b4` | `2bebf26d1e93` | Avoid memsets in atimer.c | small-src+mergiraf? |
| `ced12fa11408` | `f49637da48a0` | Avoid memsets in charset.c | small-src+mergiraf? |
| `c72e6cdc464e` | `2ae49e734a5e` | Avoid memsets in coding.c | small-src+mergiraf? |
| `19264b6912a1` | `c763ac095e41` | adjust_glyph_matrix reallocation improvement | small-src+mergiraf? |
| `d12e8a94f704` | `e8d750af5c45` | Update src/alloc.c comments | small-src+mergiraf? |
| `4e5103a98076` | `63517a4f9f4d` | Document PTRDIFF_MAX <= SIZE_MAX assumption | small-src+mergiraf? |
| `ece22174e52d` | `cab841eacbd6` | Omit useless android_get_image casts | small-src+mergiraf? |
| `82ad01b631a4` | `267faa44e500` | Fix format typos in never-executed textconv.c | small-src+mergiraf? |
| `e7a333f18e96` | `8ed7c4328384` | EVENT_INIT via a compound literal | small-src+mergiraf? |
| `4c55d04ebe31` | `c82750e40477` | Add treesit-ready-p check back to tree-sitter major modes (bug#80909) | lisp-bugfix |
| `6932c940fda8` | `e05ea1a149f2` | Fold calls to fix_position into treesit_check_position (bug#80830) | small-src+mergiraf? |
| `7cee526a8cc4` | `8e7aca420092` | Save and restore original local keymap in grep-edit-mode | lisp-bugfix |
| `a7414f18598b` | `75393d5fc76d` | native--compile-skip-on-battery-p: Try to fix ?b, ?B conditions | lisp-bugfix |
| `2c1b45f5c562` | `0c3dbff5e213` | ; Improve documentation of 'vc-dir-auto-hide-up-to-date' | lisp+news-bug |
| `7cef36258148` | `3d7296e513d4` | Fix the Android build | small-src+mergiraf? |
| `d6215451fad2` | `57e14dce7ce9` | Fix parsing of font metadata tables on Android | small-src+mergiraf? |
| `6d15d68e1f77` | `c10e317fd2a7` | ; * src/sfntfont-android.c (GET_SCANLINE_BUFFER): Correct commentary. | small-src+mergiraf? |
| `c6181780663a` | `c4e031bf7d05` | ; Mark process-test-stderr-buffer as :unstable when running on emba | test-only |
| `ea2110b6e56e` | `c1557846eea8` | ; * src/sfntfont-android.c (GET_SCANLINE_BUFFER): Fix a typo. | small-src+mergiraf? |
| `ca5e9976b149` | `2a2f74524d74` | Pixel-direct alignment in visual-wrap-prefix-mode (bug#81039) | lisp-bugfix |
| `ea54c33950f5` | `3e9e443b2567` | ; * etc/PROBLEMS: Link to bug#81124. | doc-only |
| `967d8182cfa2` | `de63078089e1` | pgtk: Fix -Wint-conversion compilation error. | small-src+mergiraf? |
| `2e70b88623ed` | `ab6d68130459` | Fix fill-paragraph combining text with preceding comment | lisp-bugfix |
| `c3babe4b8966` | `a82d6d9290ae` | Fix lax whitespace highlight during query-replace | lisp-bugfix |
| `6728239f32f7` | `0638e796694d` | Use compound literal in lisp_h_make_fixnum_wrap | small-src+mergiraf? |
| `69286be27db3` | `a95412df64d3` | ; Fix an overwide docstring line. | lisp-doc-style |
| `545bbc6ebe81` | `93dc2ae1e8fa` | widget-image-find: Use 'image-load-path' (bug#81140) | lisp-bugfix |
| `4870bc06fa36` | `84ff3b727a9a` | ses doc, add comment how to compile individually the manuals. | doc-only |
| `24879846852a` | `0e48c1cd2192` | * lisp/shell.el (shell): Fix typo: use process-live-p (bug#81145). | lisp-bugfix |
| `2955b51e80c1` | `878860623dde` | ; * etc/NEWS: Document the change in mode-line faces. | doc-only |
| `69fd4b87f4db` | `750e33643398` | Don't make buffer read-only when reverting if 'view-mode' was disabled | lisp-bugfix |
| `72d890c43e70` | `bec978520c57` | ; Update the documentation of 'debug' | doc-only |
| `8902361cba86` | `1994a04a2cc1` | README for manual translations available, and how to compile them | doc-only |

## Needs review (grouped by area)

### src/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `1fae14a022f8` | Streamline styled_format aux allocation | 35 | unclassified |
| `efb83df33142` | Don’t trust RLIMIT_NOFILE in src/process.c | 115 | unclassified |
| `cda03bebfc06` | Improve w32 implementations of 'signal' and 'raise' | 66 | missing-file:src/w32proc.c |
| `1eb2e052bb55` | New function memory_full_up | 131 | missing-file:src/haikufns.c |
| `59b2f8f1dc45` | Plug default_PATH memory leak | 21 | unclassified |
| `4d85084509a1` | Fix unlikely json.c size overflow calculations | 86 | unclassified |
| `64eb869b6883` | Be more careful about size multiplication | 81 | src-multi-file |
| `1bee33c1c801` | sfnt_parse_languages does not need USE_SAFE_ALLOCA | 41 | unclassified |
| `fbd2f781b2a7` | Be more careful about X selection sizes | 29 | unclassified |
| `2e91ed5f129a` | Prefer ptrdiff_t to size_t when either will do | 153 | src-multi-file |
| `7e0d4fae01f2` | Simplify sfnt.c by using long long | 353 | large |
| `c4e20777c265` | Better size overflow checking for sfnt.c | 278 | large |
| `7bfde4d50b5e` | sfnt.c eassert vs assert | 22 | unclassified |
| `c146e3643c4e` | Fix off-by-one error in 'styled_format' | 11 | src-multi-file |
| `94dbab2fe45f` | Fix 'do_casify_natnum' for events with all flags set | 11 | src-multi-file |
| `7f8ac8bf6f04` | Avoid crash in self-insert-command for peculiar arguments | 11 | src-multi-file |
| `b72dcebdabfc` | Avoid crash in self-insert-command with non-ASCII auto-fill | 19 | src-multi-file |
| `689448a0418d` | Unbreak MS-Windows build broken by Gnulib sync | 41 | src-multi-file |
| `54b6ea14a928` | Port MinGW GCC 9.2 image.c fix to non MS-Windows | 28 | src-multi-file |
| `7ee331439811` | Speed-up cursor motion under 'display-line-numbers-mode' | 63 | src-multi-file |

### lisp/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `1754015c6034` | Improve auth-source-backend-parse | 23 | lisp-no-bug |
| `7892ae5eaf4c` | Fix pathological slowness in flex completion | 21 | lisp+src |
| `0a5e69eaef78` | lisp/visual-wrap.el (visual-wrap--content-prefix): Adjust doc | 5 | lisp-no-bug |

### lisp/emacs-lisp/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `e0fbecaf658b` | Adapt ert-remote-temporary-file-directory settings | 13 | lisp-no-bug |
| `7fe595465bcc` | vc-refresh-state: Use cond* | 117 | lisp-no-bug |
| `72b50901ef95` | lisp/emacs-lisp/package.el (package-quickstart-refresh): Delete stale elc | 4 | lisp-no-bug |

### lisp/gnus/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `142b1e0d4c3f` | Fix Lisp injection via X-Draft-From in Gnus | 2 | lisp-no-bug |
| `02fb01166eb5` | Gnus: Prefer passing functions to message-add-action | 45 | lisp-no-bug |

### lisp/mail/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `4d87d203cfb9` | Fix display of inline SVG images in Rmail | 7 | lisp-no-bug |

### lisp/progmodes/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `389874c533bb` | Eglot: unbreak for treesit-less builds | 16 | lisp-no-bug |
| `9436d92c5daa` | Eglot: fix eglot--format-makrup when MARKUP just a string | 2 | lisp-no-bug |
| `8f31ccbf823b` | Eglot: announce markdown support for completion docs | 1 | lisp-no-bug |
| `217064e9dca2` | ;cperl-mode.el: Fix fontification edge cases | 69 | lisp-no-bug |

### lisp/textmodes/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `133d1d591cb9` | markdown-ts-mode: align default face definitions with markdown-mode | 54 | lisp-no-bug |
| `36c690861656` | Refactor reftex-isearch-minor-mode to use define-minor-mode | 75 | lisp-no-bug |
| `a2379402fc9d` | (reftex-isearch-minor-mode): A few more simplifications | 18 | lisp-no-bug |

### lisp/vc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `28a13b01c7d7` | vc-refresh-state: Override default-directory for backend functions | 14 | lisp-no-bug |

### doc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `0d5680665bc1` | Etags handling of fortran files (bug#81086). | 12 | unclassified |
| `7df8604ea635` | ; Improve documentation of lazy-highlight in search and replace commands | 65 | lisp-multi-area |
| `3d2bb233f27c` | ; Minor Tramp changes | 39 | lisp-multi-area |
| `833553dd9aec` | dbus-call-method-asynchronously supports also an ERROR-HANDLER | 238 | large |
| `c4803e57c8c0` | ; * doc/translations/fr/info_common.mk: Fix typos. | 6 | missing-file:doc/translations/fr/info_common.mk |

### etc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `e381cf1fc97f` | Allow child processes to continue after EPIPE | 135 | lisp+src |
| `741feca4972a` | New tool bar icons for artist-mode | 1566 | feature |
| `eb653865c3a3` | markdown-ts-mode: Don't enable unconditionally by default | 41 | lisp-multi-area |
| `64f4ce7b2d9d` | Allow optionally disabling the use of TABs for TTY cursor movement | 28 | src-multi-file |

### lib-src/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `25a07c30e5e1` | Don’t use VLA in etags.c mercury_decl | 38 | unclassified |
| `17215532dc72` | Avoid a memset in emacsclient get_server_config | 10 | unclassified |
| `52ccc1b8d389` | Avoid memsets in pop.c | 17 | unclassified |
| `02897e208d00` | emacsclient quote_argument is void | 2 | unclassified |

### admin/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `225876e97999` | ARRAYELTS → countof | 344 | missing-file:admin/merge-gnulib |

### other

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `4f13f52a3aad` | * build-aux/git-hooks/commit-msg: Replace Markdown-style quotation. | 16 | unclassified |
| `3461b450c5ea` | Don’t silently truncate file names in exec.c | 98 | unclassified |
| `1e0b0bed2874` | Avoid a memset in allocate_widget_instance | 4 | missing-file:lwlib/lwlib.c |
| `44013f6be751` | Revert "Don’t silently truncate file names in exec.c" | 98 | unclassified |
| `5d8bb14d3b90` | Omit useless casts found by GCC 16 | 299 | missing-file:lwlib/xlwmenu.c |
| `b174382a2dfa` | Also copy lib/mini-gmp-gnulib.c from Gnulib | 4 | unclassified |
| `330b4e2a942a` | Fix the Android build again | 18 | unclassified |
| `de926d281a11` | Fix the MSDOS build | 31 | missing-file:config.bat |
| `d8933b9f0747` | Fix the MSDOS build | 5 | missing-file:msdos/sedlibmk.inp |
| `5eaacff65b7c` | Add a checking/result message for DOCLANGS derivation. | 2 | missing-file:m4/texinfo.m4 |
| `02c806cb4747` | Use a shell function to delay message. | 25 | missing-file:m4/texinfo.m4 |
| `5c36f6c22835` | Fix overquoting in gl_SET_MAKEINFO | 6 | missing-file:m4/texinfo.m4 |
| `1f662e2ab704` | ; * m4/texinfo.m4 (gl_SET_MAKEINFO): Fix introductory comment. | 3 | missing-file:m4/texinfo.m4 |

## Failed (cherry-pick aborted)

| SHA | Subject | Conflict |
|---|---|---|
| `24f9e6a69362` | Make styled_format more compatible with igc | conflict:src/editfns.c |
| `d4cb550dba6c` | ; Improve last change | conflict:test/src/process-tests.el |
| `c80d22dcfcc3` | Remove stray inrange_pipe comment | conflict:src/process.c |
| `25fb3f9b467c` | Fix self-insert-command in multibyte buffers (bug#81129) | conflict:src/cmds.c |

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
| `ad8af430e6c8` | Avoid a memset in alloc-colors.c | admin |
| `768c8bf00455` | Revert "* admin/notes/documentation: Recommend not using "it's"." | admin |
| `6fb6a4f76ddc` | Pacify GCC better when building the test module | autotools |
| `834ff524f980` | Update from Gnulib by running admin/merge-gnulib | autotools |
| `3621ef5c4205` | Add dependance of info file on source. | autotools |
| `0275b41d1c61` | Generate manual for other languages than default. | autotools |
| `ca346be53c70` | Handle the info duplicate target issue as close as possible to the conflict. | autotools |
| `2455b32dd316` | Move Texinfo related autoconf code to a new separate texinfo.m4 file. | autotools |
| `e3b2d6f86291` | Set DOCLANGS with autoconf depending on texinfo.tex/texindex versions. | autotools |
| `31ee3253523d` | Fix build outside source directory | autotools |
| `085eeb1bddea` | Fix rules in doc/misc/Makefile.in | autotools |
| `3a0bce8f0283` | ; Fix a recent change | autotools |
| `75153f7b7693` | Fix clash with locale variable | autotools |
| `c44f7ada0c01` | Avoid using the LANG environment variable | autotools |
| `3d01d53c1e34` | Make doc/ build fail on DOCLANG=dummy | autotools |
| `35af8d1099e2` | Make build in doc/ happen in parallel over DOCLANGS | autotools |


## Manual triage (post-run) — 2026-05-31 evening

Following the auto-run, all 64 REVIEW + 4 FAILED commits were analyzed via three
parallel subagents and acted on individually.

**Counts**: applied 52 (45 clean + 3 NEWS-redirect + 3 manual conflict
resolution + 1 partial) · skipped 12 · deferred 4.

### Manually applied (cleanly)

| Original SHA | New SHA | Subject |
|---|---|---|
| `1fae14a022f8` | `84f244dc821e` | Streamline styled_format aux allocation |
| `24f9e6a69362` | `d1d674bcbde3` | Make styled_format more compatible with igc (was FAILED — unblocked by 1fae14a) |
| `d4cb550dba6c` | `3155327b1787` | ; Improve last change (was FAILED — unblocked by e381cf1f) |
| `389874c533bb` | `70ec1963bf61` | Eglot: unbreak for treesit-less builds |
| `28a13b01c7d7` | `362e2e248340` | vc-refresh-state: Override default-directory for backend functions |
| `9436d92c5daa` | `105bc720bfd1` | Eglot: fix eglot--format-makrup when MARKUP just a string |
| `c80d22dcfcc3` | `582c4407db7f` | Remove stray inrange_pipe comment (was FAILED — unblocked by efb83df) |
| `133d1d591cb9` | `845aae20e7bc` | markdown-ts-mode: align default face definitions with markdown-mode |
| `8f31ccbf823b` | `acdf49fcdffc` | Eglot: announce markdown support for completion docs |
| `1754015c6034` | `4b5fc2ae7fde` | Improve auth-source-backend-parse |
| `0d5680665bc1` | `581d73eba29e` | Etags handling of fortran files (bug#81086) |
| `7df8604ea635` | `bf86412dd437` | ; Improve documentation of lazy-highlight in search and replace commands |
| `e0fbecaf658b` | `f1a581dbe724` | Adapt ert-remote-temporary-file-directory settings |
| `142b1e0d4c3f` | `8a78ed766b10` | Fix Lisp injection via X-Draft-From in Gnus |
| `3d2bb233f27c` | `e3d5a3f918af` | ; Minor Tramp changes |
| `741feca4972a` | `7781c27d6b73` | New tool bar icons for artist-mode |
| `7fe595465bcc` | `ad1b8df1d97d` | vc-refresh-state: Use cond* |
| `eb653865c3a3` | `9d5af89ba94b` | markdown-ts-mode: Don't enable unconditionally by default |
| `4f13f52a3aad` | `17b98525ae92` | * build-aux/git-hooks/commit-msg: Replace Markdown-style quotation |
| `59b2f8f1dc45` | `c7985aa50c43` | Plug default_PATH memory leak |
| `4d85084509a1` | `6553ac69c322` | Fix unlikely json.c size overflow calculations |
| `25a07c30e5e1` | `10f5d480923a` | Don't use VLA in etags.c mercury_decl |
| `17215532dc72` | `a1d44637994c` | Avoid a memset in emacsclient get_server_config |
| `52ccc1b8d389` | `f09a0e770059` | Avoid memsets in pop.c |
| `64eb869b6883` | `c057cbbae198` | Be more careful about size multiplication |
| `1bee33c1c801` | `fddb3b2d9da9` | sfnt_parse_languages does not need USE_SAFE_ALLOCA |
| `fbd2f781b2a7` | `3b8478cb7c7a` | Be more careful about X selection sizes |
| `2e91ed5f129a` | `3c2cba1bab43` | Prefer ptrdiff_t to size_t when either will do |
| `7e0d4fae01f2` | `c3373280b94c` | Simplify sfnt.c by using long long |
| `7892ae5eaf4c` | `e511e2f8aabe` | Fix pathological slowness in flex completion |
| `4d87d203cfb9` | `ee70171fdee4` | Fix display of inline SVG images in Rmail |
| `c146e3643c4e` | `21b7b190ab70` | Fix off-by-one error in 'styled_format' |
| `94dbab2fe45f` | `f99c59c793a1` | Fix 'do_casify_natnum' for events with all flags set |
| `7f8ac8bf6f04` | `97a89ef0d506` | Avoid crash in self-insert-command for peculiar arguments |
| `b72dcebdabfc` | `8142d0f8f971` | Avoid crash in self-insert-command with non-ASCII auto-fill |
| `217064e9dca2` | `cdb101ef7bb7` | ;cperl-mode.el: Fix fontification edge cases |
| `72b50901ef95` | `2c07e7258343` | package.el (package-quickstart-refresh): Delete stale elc |
| `25fb3f9b467c` | `b58df4c353f1` | Fix self-insert-command in multibyte buffers (bug#81129) (was FAILED — unblocked by 7f8ac8/b72dceb) |
| `02fb01166eb5` | `539e6055de73` | Gnus: Prefer passing functions to message-add-action |
| `02897e208d00` | `079c820f76e7` | emacsclient quote_argument is void |
| `b174382a2dfa` | `b0f8fc6ad22f` | Also copy lib/mini-gmp-gnulib.c from Gnulib |
| `7ee331439811` | `9b594876113e` | Speed-up cursor motion under 'display-line-numbers-mode' |
| `0a5e69eaef78` | `d6f68933f79a` | lisp/visual-wrap.el: Adjust doc |
| `36c690861656` | `dc8ea5daca54` | Refactor reftex-isearch-minor-mode to use define-minor-mode |
| `a2379402fc9d` | `1a1fd611f2ca` | (reftex-isearch-minor-mode): A few more simplifications |

### Applied with NEWS → NEWS.31 redirect

Upstream's `etc/NEWS` (now an Emacs 32.1 file) was too divergent from our
`etc/NEWS.31` for Git's rename detection to route hunks automatically. The
NEWS entry was hand-ported into the matching section of `etc/NEWS.31`.

| Original SHA | New SHA | Subject |
|---|---|---|
| `e381cf1fc97f` | `8e1c341bde40` | Allow child processes to continue after EPIPE — Changes in 31.1 |
| `833553dd9aec` | `4bf3e3160827` | dbus-call-method-asynchronously supports also an ERROR-HANDLER — Lisp Changes in 31.1 |
| `64f4ce7b2d9d` | `15741764fd3d` | Allow optionally disabling the use of TABs for TTY cursor movement — Changes in 31.1 |

### Applied with manual conflict resolution

| Original SHA | New SHA | Subject | Resolution |
|---|---|---|---|
| `efb83df33142` | `e97390a6f40a` | Don't trust RLIMIT_NOFILE in src/process.c | Took upstream's `inrange_pipe` call, dropped the `#ifndef WINDOWSNT` guard (this fork already removed the WINDOWSNT guards around `create_process` pipe setup). |
| `c4e20777c265` | `6a1c39864475` | Better size overflow checking for sfnt.c | Combined upstream's switch to `directory->length - required < map_size` with the second-line `ckd_add (&data_size, map_size, directory->length)` already in HEAD from the earlier-applied `d6215451fad` Android meta-table fix. |
| `7bfde4d50b5e` | `74cc365f3403` | sfnt.c eassert vs assert | This fork had wrapped four `assert(start <= row_end)` calls in `#ifndef NDEBUG ... #endif`; replaced each with upstream's `eassert(...)` — `eassert` already handles the NDEBUG case. |

### Applied partially

| Original SHA | New SHA | Subject | Hunks dropped |
|---|---|---|---|
| `1eb2e052bb55` | `9bbaeeb662fb` | New function memory_full_up | Dropped `src/haikufns.c`, `src/haikufont.c`, `src/haikuselect.c`, `src/haikuterm.c`, `src/w32term.c` hunks — those files are not present in this fork. Committed without the `(cherry picked from ...)` trailer because `git commit -C` was used instead of `cherry-pick --continue`; note that future runs of the skill will re-classify this commit as REVIEW via the patch-id mismatch and must be skipped manually. |

### Skipped — not applicable to this fork

| SHA | Subject | Reason |
|---|---|---|
| `cda03bebfc06` | Improve w32 implementations of 'signal' and 'raise' | Touches only `src/w32proc.c`; not present in this fork. |
| `3461b450c5ea` + `44013f6be751` | Don't silently truncate file names in exec.c (apply/revert pair) | Net no-op; revert's rationale (intprops.h unavailable from `exec/`) still applies here. |
| `1e0b0bed2874` | Avoid a memset in allocate_widget_instance | Only touches `lwlib/lwlib.c`; not present in this fork (NS-only build). |
| `689448a0418d` | Unbreak MS-Windows build broken by Gnulib sync | MS-Windows + MSDOS only. |
| `de926d281a11`, `d8933b9f0747` | Fix the MSDOS build | MSDOS only (`config.bat`, `msdos/sedlibmk.inp`). `d8933b9` upstream subject says "Do not merge to master". |
| `5eaacff65b7c`, `02c806cb4747`, `5c36f6c22835`, `1f662e2ab704` | `m4/texinfo.m4` series | autotools removed from this fork. |
| `c4803e57c8c0` | doc/translations/fr/info_common.mk typo fix | French translation Makefile not present in this fork's doc tree. |

### Deferred — applies but skipped this round

| SHA | Subject | Reason |
|---|---|---|
| `225876e97999` | ARRAYELTS → countof | Sweep across 50+ files we ship, but depends on a Gnulib `stdcountof.h` module that this fork would need to bundle (no `admin/merge-gnulib`) and wire into Meson. A future commit should either land `stdcountof.h` first, or convert only call sites that can use a local `#define`. |
| `330b4e2a942a` | Fix the Android build again | Re-adds local `ARRAYELTS` for `exec/trace.c` because the exec helper can't use Gnulib. Only meaningful AFTER `225876e9` lands; pair them. |
| `5d8bb14d3b90` | Omit useless casts found by GCC 16 | Large GCC-16 cleanup; the `lwlib/xlwmenu.c` portion drops cleanly for this fork but the remainder still touches ~33 files. Worth a focused partial-apply pass later. |
| `54b6ea14a928` | Port MinGW GCC 9.2 image.c fix to non MS-Windows | Introduces `PIX_CONTAINER_TO_CONTEXT` macro; this fork's `image.c` doesn't use the macro pattern and the benefit is small. Low ROI for this fork. |
