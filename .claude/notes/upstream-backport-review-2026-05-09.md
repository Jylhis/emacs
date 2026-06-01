# Upstream backport review — 2026-05-09

- Anchor commit: `08a22b8965eca05982be748f768d92bc6f299051` (; Don't skip 'vc-test-src-version-diff' test)
- Range: `08a22b8965ec..emacs-upstream/master`
- Reviewed: 141   Applied: 18   Needs review: 111   Skipped: 12

## Applied

| Original SHA | New SHA | Subject | Bucket |
|---|---|---|---|
| `7017fcc4c5d1` | `4c15ad0293e8` | ; Add new test to files-tests | test-only |
| `8c8a43bc5455` | `0fd30482fa5d` | Fix warning when building Calc manual | doc-only |
| `27a18cfd7e39` | `418398556aff` | Add ERT coverage for read_key_sequence behaviour | test-only |
| `6731146e44bc` | `f9b85c57eb45` | ; * doc/misc/calc.texi (Top): Improve menu item description (bug#80923). | doc-only |
| `f6d404145ed0` | `89a6c196e1da` | Precise quoting of file names with a leading tilde | doc-only |
| `40b6f0180b37` | `6b78af561912` | ; Tweak some ERC tests and related utilities | test-only |
| `1b14d6f92b1b` | `5a68200e993e` | * src/.gdbinit: Ignore SIGPIPE.  (Bug#80911) | small-c-fix |
| `b376c405aa8d` | `2231981216d1` | ; Add a test for sqlite-close | test-only |
| `963d2ebffbfc` | `8494b86d1db0` | ; * doc/lispintro/emacs-lisp-intro.texi: Update *Backtrace* outputs. | doc-only |
| `a1739bc75e1b` | `4f2fdfeee23d` | ; * doc/translations/fr/misc/ses-fr.texi: Typo. | doc-only |
| `e24d9232e035` | `88f05ec4bbed` | Jsonrpc: add new tests using Python subprocesses | test-only |
| `9c0a699c59eb` | `741cc500d832` | Adaot tramp-tests.el | test-only |
| `14f17722aaf3` | `215ab8d48425` | Fix flicker of child frame right after make-frame-visible | small-c-fix |
| `174f75f88893` | `cd49f625f106` | ; Fixes to Acknowledgments lists. | doc-only |
| `838fc3547aa2` | `b564dcd02a7e` | ; * doc/emacs/emacs.texi (Acknowledgments): Fill. | doc-only |
| `fdab8a91858f` | `00b2e698ee0c` | ; Revert Eric's commits from February. | test-only |
| `4beb8e89636b` | `96d48420268e` | Fix infloop in redisplay due to continuation glyphs | small-c-fix |
| `edd345c33ffa` | `a25e08c03e1d` | ; Move etc/NEWS to etc/NEWS.31. | doc-only |

## Needs review

| SHA | Subject | Files | Why |
|---|---|---|---|
| `153809088915` | (completion--file-name-table): Improve completion of `/a/~b/c` | lisp/minibuffer.el | unclassified |
| `046db6404426` | Call format-spec substitution functions in current buffer | lisp/format-spec.el | unclassified |
| `800a272b6259` | Fix defining a few faces as empty | lisp/net/shr.el, lisp/nxml/nxml-mode.el, lisp/progmodes/make-mode.el | unclassified |
| `42f6459bad07` | Set indent property for with-connection-local-variables | lisp/files-x.el | unclassified |
| `977a7607b648` | Use plain autoload cookie with transient-define-prefix | lisp/international/emoji.el | unclassified |
| `8b41b66e6fe8` | ; * lisp/treesit.el (treesit-buffer-root-node): Fix docstring. | lisp/treesit.el | unclassified |
| `09f8ce0f5295` | Better heuristic in treesit-font-lock-fontify-region in multi-parser | lisp/treesit.el | unclassified |
| `d969185878bf` | Use treesit-language-available-p for language check (bug#80909) | lisp/treesit.el | unclassified |
| `071fdf27510f` | ; Avoid byte-compilation warnings in transient.el. | lisp/transient.el | unclassified |
| `3897a808d920` | ; Fix an inconsistency in C symbol naming | src/xfns.c | unclassified |
| `4477ade0fa4a` | lisp/emacs-lisp/crm.el (crm-complete-and-exit): Simplify docstring | lisp/emacs-lisp/crm.el | unclassified |
| `7de1d99d3a9f` | In fido-vertical-mode, let C-s and C-r recover their original use | lisp/icomplete.el | unclassified |
| `dee5ca5acd33` | ; Avoid mutation in string-collate-lessp example. | src/fns.c | unclassified |
| `ae40c3a43862` | New commands to report diffs of all local changes | doc/emacs/maintaining.texi, etc/NEWS, lisp/vc/vc-dir.el, lisp/vc/vc-hooks.el, lisp/vc/vc.el | unclassified |
| `7d9dad424143` | New VC commands for remote unintegrated changes | doc/emacs/vc1-xtra.texi, etc/NEWS, lisp/vc/vc-dir.el, lisp/vc/vc-hooks.el, lisp/vc/vc.el | unclassified |
| `e452c4a59fb8` | ; Update ldefs-boot.el. | lisp/ldefs-boot.el | unclassified |
| `f06786499e59` | Make TS query cache work, grow less | lisp/treesit.el | unclassified |
| `d278e51f43c5` | (loaddefs-generate--make-autoload): Fix autoload for `emoji-insert` | lisp/emacs-lisp/loaddefs-gen.el | unclassified |
| `4e420d0b20eb` | In tree-sitter, signal if predicate function causes reparse | src/treesit.c | unclassified |
| `d2d49057eb43` | ; * lisp/treesit.el (treesit-ready-p): Fix docstring. | lisp/treesit.el | unclassified |
| `3ce42ffd609c` | ; * src/treesit.c (treesit_pred_with_guard): Fix style conventions. | src/treesit.c | unclassified |
| `4fcc8a473a19` | ; Spelling fixes. | ChangeLog.4, doc/misc/org.org, etc/NEWS, etc/themes/modus-themes.el, lisp/calendar/diary-icalendar.el, … | unclassified |
| `51ae6e12b922` | Pacify -Wunused-but-set-variable from gcc 16 and clang 13 | src/coding.c | unclassified |
| `17f755366efc` | ; Fix shortdoc for seq-concatenate (bug#80810). | lisp/emacs-lisp/shortdoc-doc.el | unclassified |
| `a0b7ae5abf88` | eww-handle-link: Split HTML rel on spaces | lisp/net/eww.el | unclassified |
| `978c14b13189` | cl-lambda-list, cl-lambda-list1: Fix &key spec | lisp/emacs-lisp/cl-macs.el | unclassified |
| `2db707cfd23e` | (seq-concatenate): Fix docstring (bug#80810) | lisp/emacs-lisp/seq.el, lisp/emacs-lisp/shortdoc-doc.el | unclassified |
| `b4e128b0cb25` | ; * lisp/emacs-lisp/let-alist.el (let-alist): Fix typo. | lisp/emacs-lisp/let-alist.el | unclassified |
| `b54cde91194e` | Fix value of 'default-line-height' | lisp/simple.el | unclassified |
| `a24ff52a79b4` | New variable 'completion-preview-is-calling' | etc/NEWS, lisp/completion-preview.el | unclassified |
| `c7bca9f34052` | Define variable alias for erc-completion-mode | lisp/erc/erc-pcomplete.el | unclassified |
| `ba2a15074069` | Restore erc-last-saved-position from previous session | lisp/erc/erc-log.el, test/lisp/erc/erc-scenarios-log.el, test/lisp/erc/resources/join/reconnect/foonet-again.eld | unclassified |
| `cf9728c4be8f` | Only perform erc-log-insert-log-on-open setup once | etc/ERC-NEWS, lisp/erc/erc-log.el, test/lisp/erc/erc-scenarios-log-options.el | large |
| `da4ab3d7381e` | Pacify GCC 16.0.1 -Wanalyzer-null-dereference in xdisp.c | src/xdisp.c | unclassified |
| `a6a3b32208c5` | Try to resize or resize-and-move child frames in one update | src/gtkutil.c, src/widget.c, src/xdisp.c, src/xfns.c, src/xterm.c | unclassified |
| `83b19f4d0f40` | Don't wait out the whole event timeout unnecessarily | src/androidterm.c, src/xterm.c | unclassified |
| `049a94b4e565` | Remove the effect of x_gtk_resize_child_frames=hide | src/gtkutil.c, src/pgtkfns.c, src/xfns.c | unclassified |
| `73fe7a7097da` | Simplify the fullscreen adjustment in xg_frame_set_char_size | src/gtkutil.c | unclassified |
| `6cd5b16dd0e9` | Resize child frames with GTK3 immediately too | src/gtkutil.c | unclassified |
| `19696dbc24fc` | ; Add comment thing for c-ts-mode | lisp/progmodes/c-ts-mode.el | unclassified |
| `dd3f0053d251` | ; (external-completion-table): Fix a couple of typos. | lisp/external-completion.el | unclassified |
| `d80c9e534d78` | ; project.el: Use when-let* not if-let* where appropriate. | lisp/progmodes/project.el | unclassified |
| `6583cc4fdfc4` | Update to Transient v0.13.1-10-gc168d396 | doc/misc/transient.texi, lisp/transient.el | unclassified |
| `92788f3be43b` | Update to Transient v0.13.2-10-gf7894ca4 | doc/misc/transient.texi, lisp/transient.el | unclassified |
| `17f9f0c97d34` | * etc/themes/newcomers-presets-theme.el: Fix checkdoc issue | etc/themes/newcomers-presets-theme.el | unclassified |
| `87da929eb50c` | Don't break line when inserting <code> tags | lisp/textmodes/sgml-mode.el | unclassified |
| `cb21b7d71f4e` | Mark myself as maintainer of sgml-mode | admin/MAINTAINERS, lisp/textmodes/sgml-mode.el | unclassified |
| `4795e83a6948` | Project prompters always default to current project, if any | etc/NEWS, lisp/progmodes/project.el, lisp/vc/vc.el | unclassified |
| `2207a588997c` | Eglot: find well behaved UTF char for code actions (bug#80326) | lisp/progmodes/eglot.el | unclassified |
| `e575817e8fef` | ; Improve documentation of Emacs server-client protocol | lib-src/emacsclient.c, lisp/server.el | unclassified |
| `25659d5a75e8` | ; * lisp/emacs-lisp/pcase.el (pcase-exhaustive): Doc fix. | lisp/emacs-lisp/pcase.el | unclassified |
| `0d0891c1bb8a` | ; Fix an issue with counting glyphs on TTY frames | src/dispnew.c | unclassified |
| `d51a4722316e` | ; * src/sfnt.c (sfnt_read_name_table): Avoid 32-bit overflow. | src/sfnt.c | unclassified |
| `939e5956d98e` | Demote 'completion-preview-is-calling' | etc/NEWS, lisp/completion-preview.el | unclassified |
| `e42072593583` | ; * lisp/emacs-lisp/subr-x.el (work-buffer--release): Autoload (bug#80947). | lisp/emacs-lisp/subr-x.el | unclassified |
| `e05fab5775c9` | Fix 'vc-dir-resynch-file' (bug#80803) | lisp/vc/vc-dir.el | unclassified |
| `7c7081606683` | Remove 'completion-preview--is-calling' | lisp/completion-preview.el | unclassified |
| `d0f72ef86492` | Gnus logo in server buffer's mode line (bug#80850) | lisp/gnus/gnus-srvr.el, lisp/gnus/gnus-sum.el, lisp/gnus/gnus.el | unclassified |
| `5beeb4446f14` | * lisp/treesit.el (treesit-outline-level): Add guard condition. | lisp/treesit.el | unclassified |
| `e682959b6b05` | (package--builtin-alist): Don't use `defconst` since we later change it | lisp/emacs-lisp/package.el | unclassified |
| `fe58f45782cb` | Allow changing SGML "quick keys" after loading sgml-mode.el | lisp/textmodes/sgml-mode.el | unclassified |
| `7a710c3c0e85` | Allow setting 'sgml-xml-mode' buffer locally | lisp/textmodes/sgml-mode.el | unclassified |
| `dbc2e073c055` | Refine SGML offset user option types | lisp/textmodes/sgml-mode.el | unclassified |
| `c704ae0ffc5a` | Implement 'sgml-name-8bit-mode' as a proper minor mode | lisp/textmodes/sgml-mode.el | unclassified |
| `77e968b97c07` | Raise an error if 'sgml-validate-command' is not configured | lisp/textmodes/sgml-mode.el | unclassified |
| `29f2c6eee030` | Use 'read-shell-command' to read SGML validation command | lisp/textmodes/sgml-mode.el | unclassified |
| `9f6cf73b8e69` | Prevent indentation within whitespace sensitive HTML tags | lisp/textmodes/sgml-mode.el | unclassified |
| `f2de11f1f030` | Add for <details> to 'html-tag-alist' and 'html-tag-help' | lisp/textmodes/sgml-mode.el | unclassified |
| `75a36bde59fc` | Add for <picture> to 'html-tag-alist' and 'html-tag-help' | lisp/textmodes/sgml-mode.el | unclassified |
| `9be140466a5a` | Ensure package archives are loaded for 'package-isolate' | lisp/emacs-lisp/package.el | unclassified |
| `9ff07688046d` | Re-add a call to clear_under_internal_border in clear_garbaged_frames | src/xdisp.c | unclassified |
| `9b3855e164de` | Jsonrpc: rework sync request handling (bug#80623) | lisp/jsonrpc.el | unclassified |
| `a952324e9be3` | keyboard.c: Allow SIGINT to `quit` in batch mode, instead of exit | doc/emacs/cmdargs.texi, etc/NEWS, src/keyboard.c, test/src/keyboard-tests.el | unclassified |
| `bc4a4500fc7e` | lisp/emacs-lisp/lisp-mode.el (lisp-fdefs): Avoid obsolete "face vars" | lisp/emacs-lisp/lisp-mode.el | unclassified |
| `ed1fe2ca9590` | nadvice.el: Make it easier to find how to change an interactive-form | doc/lispref/functions.texi, etc/NEWS, lisp/emacs-lisp/nadvice.el | unclassified |
| `b20307c4c789` | ; Fix doc strings of timer-set-* functions | lisp/emacs-lisp/timer.el | unclassified |
| `151ea29a8e2f` | ; Fix doc string of 'elisp-fontify-semantically' (bug#80948) | lisp/progmodes/elisp-mode.el | unclassified |
| `b36a26bb3b81` | Improve 'markdown-ts-mode' | lisp/textmodes/markdown-ts-mode-x.el, lisp/textmodes/markdown-ts-mode.el | large |
| `c878753d3964` | Accept stream type as 4th argument of X-Message-SMTP-Method header | doc/misc/message.texi, lisp/gnus/message.el | unclassified |
| `d24b10ca75f4` | Introduce 'margin' face for window margin background | doc/lispref/display.texi, etc/NEWS, lisp/faces.el, src/dispextern.h, src/xdisp.c, … | large |
| `d48b7745247a` | ; Fix last change | src/xdisp.c | unclassified |
| `47e014ff90ef` | ; Fix byte-compilation warnings in markdown-ts-mode | lisp/textmodes/markdown-ts-mode-x.el, lisp/treesit.el | unclassified |
| `288f8d0b0529` | ; (elisp-fontify-symbol): Improve docstring. | lisp/progmodes/elisp-mode.el | unclassified |
| `5789621632aa` | elisp-mode: Cache 'help-echo' function results (bug#80948) | lisp/progmodes/elisp-mode.el | unclassified |
| `8f9607d53223` | vc-finish-logentry: Skip displaying async command buffer sometimes | lisp/vc/vc-dispatcher.el | unclassified |
| `283b47ab2e38` | vc-switch-working-tree: Don't find non-VC projects | lisp/vc/vc.el | unclassified |
| `0649c501add2` | ; (elisp-scope-analyze-form): Improve docstring. | lisp/emacs-lisp/elisp-scope.el | unclassified |
| `c9078c505b01` | Improve 'context-menu-send-to' (bug#79512) | lisp/mouse.el, lisp/send-to.el | unclassified |
| `b57124b747ee` | ; More 'elisp-scope' and 'elisp-fontify-semantically' doc improvements | lisp/emacs-lisp/elisp-scope.el, lisp/progmodes/elisp-mode.el | unclassified |
| `a3f79f9da145` | ; * lisp/progmodes/elisp-mode.el (elisp-fontify-semantically): Fix typo. | lisp/progmodes/elisp-mode.el | unclassified |
| `b3b2b3de5db3` | ; * etc/NEWS: Fix typo in recent change. | etc/NEWS | conflict |
| `930f298f4d0e` | (help--symbol-completion-table): Try and fix bug#80873 | lisp/help-fns.el | unclassified |
| `61e9dfe5f7d9` | ; * lisp/treesit.el (treesit--update-ranges-local): Fix let-binding. | lisp/treesit.el | unclassified |
| `d962c83aa37e` | ; Improve doc strings of several Help-related user options | lisp/help-fns.el, lisp/help.el | unclassified |
| `dfc7cf8e4119` | ; * etc/NEWS (margin): Fix a typo, improve wording, move to proper place. | etc/NEWS | conflict |
| `eae96d9fcb8e` | Handle long environment variables in Tramp oricesses | lisp/net/tramp-sh.el, test/lisp/net/tramp-tests.el | unclassified |
| `39e15056832d` | ; Expand 'elisp-fontify-symbol' and 'elisp-scope-analyze-form' docs | lisp/emacs-lisp/elisp-scope.el, lisp/progmodes/elisp-mode.el | unclassified |
| `187efe4e312f` | ; * lisp/emacs-lisp/elisp-scope.el (elisp-scope-analyze-form): Doc fix. | lisp/emacs-lisp/elisp-scope.el | unclassified |
| `581db34a7724` | ; Fix crash in macOS Accessibility Zoom timer (bug#80624) | src/nsterm.m | unclassified |
| `6c3dc7aafd36` | [GTK3] Improve the resize -> hide -> show scenario | src/gtkutil.c | unclassified |
| `f20e3e473d10` | [GTK3] Move the frame to position before showing | src/xterm.c | unclassified |
| `0c51be894f73` | Unpreload package-activate-all | lisp/emacs-lisp/package-activate.el | unclassified |
| `f833e560c153` | Update to Transient v0.13.3-10-g87d0ca08 | doc/misc/transient.texi, lisp/transient.el | unclassified |
| `a9064bfdd9c4` | ; * lisp/term/x-win.el (icon-map-list): Fix :type (bug#80982) | lisp/term/x-win.el | unclassified |
| `2f73996647ab` | Move ns_init_colors() after init_callproc() (bug#80752) | src/emacs.c | unclassified |
| `3c6c3f5a6906` | ; Fix two file headers misunderstood by authors.el. | lisp/org/ob-ditaa.el, lisp/progmodes/lua-mode.el | unclassified |
| `48b064a2aa3b` | Fix 'vc-dir-resynch-file' again (bug#80967) | lisp/vc/vc-dir.el | unclassified |
| `060451d6e0b3` | treesit-explore-mode usability improvements (bug#80935) | lisp/treesit.el | unclassified |
| `f94637749a26` | vc-switch-working-tree: Use project-current again | lisp/vc/vc.el | unclassified |
| `69c50dcb4733` | ; package-activate-all: Drop requiring package now not preloaded. | lisp/emacs-lisp/package-activate.el | unclassified |
| `2d496b842d6c` | ; Fix Gregor Schmid's attribution for lua-mode.el. | etc/AUTHORS, lisp/progmodes/lua-mode.el | unclassified |

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
