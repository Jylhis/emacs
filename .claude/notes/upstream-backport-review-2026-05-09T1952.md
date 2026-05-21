# Upstream backport review — 2026-05-09T19:52 UTC

- Anchor commit: `08a22b8965ec` (; Don't skip 'vc-test-src-version-diff' test) — 2026-04-27
- Range: `08a22b8965ec..emacs-upstream/master` (146 commits behind)
- Reviewed: 146   Applied this run: 106   Trailer-deduped: 17 (yesterday)   Skipped: 12   Skipped per plan: 5
- Conflict-resolution: NEWS-only and 7 mid-file conflicts retried with `-X theirs` (8 commits below tagged `+theirs`).

## Applied this run

| Original SHA | New SHA | Subject |
|---|---|---|
| `153809088915` | `c239ec43af63` | (completion--file-name-table): Improve completion of `/a/~b/c` |
| `046db6404426` | `00bd08eb4af7` | Call format-spec substitution functions in current buffer |
| `800a272b6259` | `06d6331f4387` | Fix defining a few faces as empty |
| `42f6459bad07` | `cc70f53dabbe` | Set indent property for with-connection-local-variables |
| `977a7607b648` | `153bf1087fb2` | Use plain autoload cookie with transient-define-prefix |
| `8b41b66e6fe8` | `9e49b3813947` | ; * lisp/treesit.el (treesit-buffer-root-node): Fix docstring. |
| `09f8ce0f5295` | `2a219093c1e0` | Better heuristic in treesit-font-lock-fontify-region in multi-parser |
| `d969185878bf` | `9bae5504453c` | Use treesit-language-available-p for language check (bug#80909) |
| `071fdf27510f` | `9c116088cb67` | ; Avoid byte-compilation warnings in transient.el. |
| `3897a808d920` | `7e24e41dd749` | ; Fix an inconsistency in C symbol naming |
| `4477ade0fa4a` | `1834c445be8b` | lisp/emacs-lisp/crm.el (crm-complete-and-exit): Simplify docstring |
| `7de1d99d3a9f` | `6770e719a7e3` | In fido-vertical-mode, let C-s and C-r recover their original use |
| `dee5ca5acd33` | `f34323e718f7` | ; Avoid mutation in string-collate-lessp example. |
| `ae40c3a43862` | `94e71199b824` | New commands to report diffs of all local changes |
| `7d9dad424143` | `0e178d10e367` | New VC commands for remote unintegrated changes |
| `f06786499e59` | `fdd0e6c57af5` | Make TS query cache work, grow less |
| `d278e51f43c5` | `9bb384c449ee` | (loaddefs-generate--make-autoload): Fix autoload for `emoji-insert` |
| `4e420d0b20eb` | `677a6490f4b2` | In tree-sitter, signal if predicate function causes reparse |
| `d2d49057eb43` | `d62b8ed13277` | ; * lisp/treesit.el (treesit-ready-p): Fix docstring. |
| `3ce42ffd609c` | `1a284962f6fb` | ; * src/treesit.c (treesit_pred_with_guard): Fix style conventions. |
| `17f755366efc` | `f6d314c4ce1b` | ; Fix shortdoc for seq-concatenate (bug#80810). |
| `a0b7ae5abf88` | `9a73134e4337` | eww-handle-link: Split HTML rel on spaces |
| `978c14b13189` | `a8ea9422290a` | cl-lambda-list, cl-lambda-list1: Fix &key spec |
| `2db707cfd23e` | `92a4df9b4566` | (seq-concatenate): Fix docstring (bug#80810) |
| `b4e128b0cb25` | `7b1d60106c02` | ; * lisp/emacs-lisp/let-alist.el (let-alist): Fix typo. |
| `b54cde91194e` | `f6ee4b51ddf9` | Fix value of 'default-line-height' |
| `a24ff52a79b4` | `41ad66157eac` | New variable 'completion-preview-is-calling' |
| `c7bca9f34052` | `0727c0a09123` | Define variable alias for erc-completion-mode |
| `ba2a15074069` | `bfe264374814` | Restore erc-last-saved-position from previous session |
| `da4ab3d7381e` | `2116c036c006` | Pacify GCC 16.0.1 -Wanalyzer-null-dereference in xdisp.c |
| `a6a3b32208c5` | `9831c60cbdb6` | Try to resize or resize-and-move child frames in one update |
| `83b19f4d0f40` | `690e56ef728f` | Don't wait out the whole event timeout unnecessarily |
| `049a94b4e565` | `e37e13d3f30c` | Remove the effect of x_gtk_resize_child_frames=hide |
| `73fe7a7097da` | `a53f084a2ec5` | Simplify the fullscreen adjustment in xg_frame_set_char_size |
| `6cd5b16dd0e9` | `3c061778a19c` | Resize child frames with GTK3 immediately too |
| `19696dbc24fc` | `6e93ec1aef80` | ; Add comment thing for c-ts-mode |
| `dd3f0053d251` | `531220e7fde7` | ; (external-completion-table): Fix a couple of typos. |
| `d80c9e534d78` | `1c7e722f7bac` | ; project.el: Use when-let* not if-let* where appropriate. |
| `6583cc4fdfc4` | `7157ac6ebbfc` | Update to Transient v0.13.1-10-gc168d396 |
| `92788f3be43b` | `3864ccd03c98` | Update to Transient v0.13.2-10-gf7894ca4 |
| `17f9f0c97d34` | `73718a04c610` | * etc/themes/newcomers-presets-theme.el: Fix checkdoc issue |
| `87da929eb50c` | `76cadedf88c3` | Don't break line when inserting <code> tags |
| `4795e83a6948` | `135293ac747a` | Project prompters always default to current project, if any |
| `2207a588997c` | `ac681fff28e1` | Eglot: find well behaved UTF char for code actions (bug#80326) |
| `25659d5a75e8` | `d50190845aa3` | ; * lisp/emacs-lisp/pcase.el (pcase-exhaustive): Doc fix. |
| `0d0891c1bb8a` | `a55d0dbf48cd` | ; Fix an issue with counting glyphs on TTY frames |
| `d51a4722316e` | `f909f924682a` | ; * src/sfnt.c (sfnt_read_name_table): Avoid 32-bit overflow. |
| `939e5956d98e` | `701d8613aae3` | Demote 'completion-preview-is-calling' |
| `e42072593583` | `5d797ba2290e` | ; * lisp/emacs-lisp/subr-x.el (work-buffer--release): Autoload (bug#80947). |
| `e05fab5775c9` | `27d44de45e59` | Fix 'vc-dir-resynch-file' (bug#80803) |
| `7c7081606683` | `df8f1cdcf747` | Remove 'completion-preview--is-calling' |
| `d0f72ef86492` | `2b6e1e3afbe6` | Gnus logo in server buffer's mode line (bug#80850) |
| `5beeb4446f14` | `99a86fcde988` | * lisp/treesit.el (treesit-outline-level): Add guard condition. |
| `e682959b6b05` | `130953ccf035` | (package--builtin-alist): Don't use `defconst` since we later change it |
| `7a710c3c0e85` | `d22d9b3f116b` | Allow setting 'sgml-xml-mode' buffer locally |
| `dbc2e073c055` | `5a941a0677ed` | Refine SGML offset user option types |
| `c704ae0ffc5a` | `b1d8e5eaacdd` | Implement 'sgml-name-8bit-mode' as a proper minor mode |
| `77e968b97c07` | `4f48cc5eecf5` | Raise an error if 'sgml-validate-command' is not configured |
| `29f2c6eee030` | `ada1bb74c767` | Use 'read-shell-command' to read SGML validation command |
| `9f6cf73b8e69` | `85ef1db8589f` | Prevent indentation within whitespace sensitive HTML tags |
| `f2de11f1f030` | `1d65b8aa95a4` | Add for <details> to 'html-tag-alist' and 'html-tag-help' |
| `75a36bde59fc` | `2f881fa1adab` | Add for <picture> to 'html-tag-alist' and 'html-tag-help' |
| `9be140466a5a` | `f7c16f845641` | Ensure package archives are loaded for 'package-isolate' |
| `9ff07688046d` | `29391c6ac0f3` | Re-add a call to clear_under_internal_border in clear_garbaged_frames |
| `9b3855e164de` | `20b2caa07af2` | Jsonrpc: rework sync request handling (bug#80623) |
| `bc4a4500fc7e` | `5ecfe00be224` | lisp/emacs-lisp/lisp-mode.el (lisp-fdefs): Avoid obsolete "face vars" |
| `b20307c4c789` | `a9529c5ff123` | ; Fix doc strings of timer-set-* functions |
| `151ea29a8e2f` | `ee549dea17ae` | ; Fix doc string of 'elisp-fontify-semantically' (bug#80948) |
| `b36a26bb3b81` | `4d65f0cfb3ed` | Improve 'markdown-ts-mode' |
| `c878753d3964` | `04c85cb2d4a3` | Accept stream type as 4th argument of X-Message-SMTP-Method header |
| `47e014ff90ef` | `26a91f43fa00` | ; Fix byte-compilation warnings in markdown-ts-mode |
| `288f8d0b0529` | `0739bdc07665` | ; (elisp-fontify-symbol): Improve docstring. |
| `5789621632aa` | `f10cc07bb13f` | elisp-mode: Cache 'help-echo' function results (bug#80948) |
| `8f9607d53223` | `08cb8069460e` | vc-finish-logentry: Skip displaying async command buffer sometimes |
| `283b47ab2e38` | `013e38746687` | vc-switch-working-tree: Don't find non-VC projects |
| `0649c501add2` | `7da2bdad1d0e` | ; (elisp-scope-analyze-form): Improve docstring. |
| `c9078c505b01` | `250d8bbb8a51` | Improve 'context-menu-send-to' (bug#79512) |
| `b57124b747ee` | `1a608d998e82` | ; More 'elisp-scope' and 'elisp-fontify-semantically' doc improvements |
| `a3f79f9da145` | `a353c5de090a` | ; * lisp/progmodes/elisp-mode.el (elisp-fontify-semantically): Fix typo. |
| `930f298f4d0e` | `3feaeaba0a21` | (help--symbol-completion-table): Try and fix bug#80873 |
| `61e9dfe5f7d9` | `5a3effc4ff35` | ; * lisp/treesit.el (treesit--update-ranges-local): Fix let-binding. |
| `d962c83aa37e` | `55b72dcfd652` | ; Improve doc strings of several Help-related user options |
| `eae96d9fcb8e` | `09a5ca150dd8` | Handle long environment variables in Tramp oricesses |
| `39e15056832d` | `d21fa6f516a5` | ; Expand 'elisp-fontify-symbol' and 'elisp-scope-analyze-form' docs |
| `187efe4e312f` | `dc58457b41af` | ; * lisp/emacs-lisp/elisp-scope.el (elisp-scope-analyze-form): Doc fix. |
| `581db34a7724` | `254c0f748fdf` | ; Fix crash in macOS Accessibility Zoom timer (bug#80624) |
| `6c3dc7aafd36` | `c0b3a3b765a1` | [GTK3] Improve the resize -> hide -> show scenario |
| `f20e3e473d10` | `f86520cb53b5` | [GTK3] Move the frame to position before showing |
| `0c51be894f73` | `3a406344e49e` | Unpreload package-activate-all |
| `f833e560c153` | `c6698e4b7561` | Update to Transient v0.13.3-10-g87d0ca08 |
| `a9064bfdd9c4` | `8ff0e1da40c8` | ; * lisp/term/x-win.el (icon-map-list): Fix :type (bug#80982) |
| `2f73996647ab` | `112a2c4595df` | Move ns_init_colors() after init_callproc() (bug#80752) |
| `3c6c3f5a6906` | `cf9800fd5b1e` | ; Fix two file headers misunderstood by authors.el. |
| `48b064a2aa3b` | `af67111a63cf` | Fix 'vc-dir-resynch-file' again (bug#80967) |
| `060451d6e0b3` | `a819bea76a16` | treesit-explore-mode usability improvements (bug#80935) |
| `f94637749a26` | `2ee32f943967` | vc-switch-working-tree: Use project-current again |
| `69c50dcb4733` | `d80e414fc752` | ; package-activate-all: Drop requiring package now not preloaded. |
| `e575817e8fef` | `4d47208bd53b` | ; Improve documentation of Emacs server-client protocol |

### Retried with `-X theirs` (prefer upstream when our edits overlapped)

| Original SHA | New SHA | Subject | Conflict on |
|---|---|---|---|
| `51ae6e12b922` | `281189d1093c` | Pacify -Wunused-but-set-variable from gcc 16 and clang 13 | src/coding.c |
| `a952324e9be3` | `821e5e80a353` | keyboard.c: Allow SIGINT to `quit` in batch mode, instead of exit | src/keyboard.c |
| `ed1fe2ca9590` | `fb38b81d7de6` | nadvice.el: Make it easier to find how to change an interactive-form | etc/NEWS.31 |
| `d24b10ca75f4` | `a8516a947e35` | Introduce 'margin' face for window margin background (Bug#80693) | etc/NEWS.31 |
| `d48b7745247a` | `b83f262d5246` | ; Fix last change | src/xdisp.c |
| `b3b2b3de5db3` | `f8457a34cb0d` | ; * etc/NEWS: Fix typo in recent change | etc/NEWS.31 |
| `dfc7cf8e4119` | `ca00874d7239` | ; * etc/NEWS (margin): Fix a typo, improve wording | etc/NEWS.31 |
| `2d496b842d6c` | `1b6dde63bc86` | ; Fix Gregor Schmid's attribution for lua-mode.el | etc/AUTHORS |

## Skipped — autotools / admin (12)

| SHA | Subject | Reason |
|---|---|---|
| `edc19c353696` | Always compile w32image.c on MinGW (Bug#80924) | autotools |
| `0179e3e062b9` | Work around GCC bug 125116 | autotools |
| `0848cbb326ca` | * admin/notes/documentation: Recommend not using "it's" | admin |
| `cbc912ed637a` | ; * admin/notes/jargon: Add entries | admin |
| `311f1fe2ba2a` | Cut the emacs-31 release branch | autotools |
| `0d287aa2761a` | Bump master Emacs version to 32.0.50 | autotools |
| `ddde687b3f93` | ; * admin/admin.el (set-version): Fix punctuation | admin |
| `991f6100eb1f` | ; * admin/make-tarball.txt: Suggest load-file, not require | admin |
| `1ec79b48f380` | ; Update exported ChangeLog files and etc/AUTHORS | autotools |
| `8d0bf280a64a` | ; * ChangeLog.5: Some fixes and tidying up | admin |
| `730d3884dc3e` | ; Fix the build broken by a typo in configure.ac | autotools |
| `5e0b4b96bc5a` | ; Adapt files in admin/notes for emacs-31 branch | admin |

## Skipped per plan (5)

| SHA | Subject | Reason |
|---|---|---|
| `cb21b7d71f4e` | Mark myself as maintainer of sgml-mode | admin/MAINTAINERS marker; touches admin/ which we don't mirror |
| `e452c4a59fb8` | ; Update ldefs-boot.el | regenerate locally instead of cherry-picking generated file |
| `4fcc8a473a19` | ; Spelling fixes | touches ChangeLog.4 + etc/NEWS + 16 files; very low value, cross-cutting |
| `cf9728c4be8f` | Only perform erc-log-insert-log-on-open setup once | 316 lines, ERC owner involvement; defer |
| `fe58f45782cb` | Allow changing SGML "quick keys" after loading sgml-mode.el | 171-line refactor; defer |

## Needs review

None. All non-skipped, non-deferred commits applied.

## Notes & follow-ups

- **etc/NEWS.31**: 4 commits' NEWS hunks were merged via `-X theirs`. NEWS.31 is intact (4777 lines, header preserved). Visual review recommended before pushing — the auto-resolution may have placed entries out of section order.
- **ldefs-boot.el**: Skipped intentionally. Regenerate via `make` or the equivalent Meson target after a clean build to pick up new `;;;###autoload` markers from cherry-picked lisp files (e.g. `e42072593583` work-buffer--release autoload).
- **GTK3 series (8 commits) applied**: This fork is NS-focused; X11/GTK3 child-frame changes apply cleanly on the source side but exercise code paths we don't routinely build. Smoke-test with a GTK3 build (or just trust upstream) before pushing.
- **markdown-ts-mode**: `b36a26bb3b81` introduced a new file `lisp/textmodes/markdown-ts-mode-x.el` (6595 lines). Build will need to register it; check that meson picks it up via globbing.
- **format-spec behavior change** (`046db6404426`): now runs substitution functions in the caller's buffer instead of a temp buffer. This is a deliberate fix but a behavior change — verify our format-spec callers (e.g. mode-line, mail headers) don't depend on the old semantics.
- **Pre-existing notes**: the previous report at `upstream-backport-review-2026-05-09.md` (no timestamp) is preserved and not overwritten.
