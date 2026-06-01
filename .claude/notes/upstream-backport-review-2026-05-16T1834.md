# Upstream backport review — 2026-05-16T1834 UTC

- Anchor: `08a22b8965ec` (; Don't skip 'vc-test-src-version-diff' test) — 2026-04-27
- Range: `08a22b8965ec..dev` vs emacs-upstream/master (221 behind)
- Reviewed: 89   Applied: 34   Retried (-X theirs): 0   Skipped: 14   Needs review: 40   Failed (conflict): 1   News-port-required: 0

## Applied

| Original SHA | New SHA | Subject | Bucket |
|---|---|---|---|
| `543d8a7a9d7e` | `23f8436ad3f2` | [NS] Fix deprecated variable (bug#80985) | small-src+mergiraf? |
| `6ba05106f4e2` | `7ae2533920a3` | Fix display images in the display margins | small-src+mergiraf? |
| `5579893ed7c7` | `957291d92f8a` | ; Don't block/unblock input in text_extents methods | small-src+mergiraf? |
| `d7c130972e08` | `56fcf722c336` | ; * lisp/term/pgtk-win.el (icon-map-list): Fix :type. | lisp-doc-style |
| `6a605c65a836` | `235cb71c7ca4` | Fix vertical-motion across overlay strings with embedded newlines | small-src+mergiraf? |
| `027043df2578` | `24e74c3a4d3c` | ; * lisp/gnus/message.el (message-server-alist): Doc fix (bug#80880). | lisp-bugfix |
| `01c5990dd064` | `ba93d573a6fa` | Fix nested read-passwd calls (bug#80838) | lisp-bugfix |
| `5323eebcffcc` | `554abe0d76a9` | Test read-passwd behavior (bug#80838) | test-only |
| `acc07f1a0301` | `eaee1bf95deb` | [GTK3] On Expose, repaint the border before the content | small-src+mergiraf? |
| `196fd80689e3` | `57c90f8d54bd` | [GTK3, HiDPI] Fix width/height round-trip through ConfigureNotify | small-src+mergiraf? |
| `f12b01582db7` | `52e4cf956b9b` | Fix Completions buffer disappearing with tmm-menubar (bug#80995) | lisp-bugfix |
| `0e7a24d93131` | `63bda451297f` | * lisp/progmodes/hideshow.el (hs--set-variable): Use 'set-local' (bug#80999) | lisp-bugfix |
| `09dc864b0b86` | `c9029db870f3` | Fix eww-submit for forms with no action (bug#80918) | lisp-bugfix |
| `20d17df3f4ff` | `8c02397e7e7f` | Use the new 'margin' face in Flymake (bug#80693) | lisp-bugfix |
| `3630baae7208` | `43de516d4314` | hideshow: Support new 'margin' face for margin indicators. (Bug#80693) | lisp-bugfix |
| `606c0b22e4ee` | `9a5ac58b9c89` | ; Make reconnect detection more readable in erc-open | lisp-doc-style |
| `ce3098752cfb` | `f671569af9dc` | doc: Remove long obsolete references to `package-initialize` | doc-only |
| `ff96db93f23d` | `ee8a742ad0e0` | keyboard-tests.el: Try and fix the failure on EMBA | test-only |
| `a00beb3a31bd` | `7d4fc22cc331` | Make 'markdown-ts-inline-images' buffer local and test for GUI (bug#80978) | lisp-bugfix |
| `0be998d4bc03` | `cc61068e17db` | Fix code-span in headings in 'markdown-ts-mode' (bug#80979) | lisp-bugfix |
| `b39c123490b3` | `49a32976a1f0` | Fix strikethrough in 'markdown-ts-mode' (bug#80991) | lisp-bugfix |
| `286833e401d7` | `ca8d5173302f` | Add read-only 'markdown-ts-view-mode' (bug#81023) | lisp-bugfix |
| `71809ee5df59` | `7aba744e37c5` | Fix 'markdown-ts-code-span' face (bug#81026) | lisp-bugfix |
| `689c3bd5088c` | `24f8e3d28701` | Use 'read-multiple-choice' in 'markdown-ts-mode' (bug#81027) | lisp-bugfix |
| `318084829c58` | `305db9a74baa` | Eglot: adjust reference to completion frontends in manual | doc-only |
| `93ea0d7d289a` | `764ea579b85a` | ; Improve documentation of VC commands in Dired | doc-only |
| `20500d62006c` | `08e3759e8f7d` | ; htmlfontify: Handle 'reset' face attribute value (bug#81032) | lisp-bugfix |
| `f4c326c378aa` | `ea3d1d07cd65` | ; * src/sfnt.c (sfnt_read_cmap_format_12): Assert there's no overflow. | small-src+mergiraf? |
| `8e3749903574` | `431d3fa393d6` | ; * doc/lispref/os.texi (Init File): Fix markup (bug#81049). | doc-only |
| `a981517b72e8` | `5151f94238d2` | Fill margins with 'margin' face on truncated screen lines | small-src+mergiraf? |
| `d3c72b83890f` | `5666499d0918` | ; * src/xdisp.c (display_line): Fix commentary (bug#80693). | small-src+mergiraf? |
| `8b6fb2f64655` | `c0d1de93a734` | ; * doc/lispref/variables.texi (Local Variables): Fix 'named-let'. | doc-only |
| `23575adc7be7` | `a4b4c0f5d7e1` | ; * doc/lispref/variables.texi (Local Variables): Fix types (bug#81004). | doc-only |
| `cf96e9cb5a5a` | `42917d11f9f4` | ; Fix byte-compilation warnings in non-Tree-Sitter builds | lisp-doc-style |

## Needs review (grouped by area)

### lisp/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `e452c4a59fb8` | ; Update ldefs-boot.el. | 112 | lisp-no-bug |
| `3b608b233edb` | Fix terminal emulation of "ESC [ K" sequence | 9 | lisp-no-bug |
| `9e4ea934f23f` | Fix 'prepare-user-lisp' to follow symlinks | 2 | lisp-no-bug |
| `c68f3237bea2` | Fix file-name-non-special implementation of get-file-buffer | 16 | lisp-no-bug |

### lisp/emacs-lisp/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `e613e38021e3` | Update "timeout" to 2.1.6 | 33 | lisp-no-bug |
| `2a166c2dbdb9` | Eldoc: display documentation in visual-line-mode | 1 | lisp-no-bug |

### lisp/erc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `6d347d983480` | Release ERC 5.6.2 | 4 | lisp-no-bug |
| `88e8b8c073e8` | ; Remove some forward declarations from ERC tests | 207 | large |
| `f3da59a8c55f` | Improve isolation of some ERC test environments | 179 | lisp-no-bug |
| `aa316285846b` | Refactor erc--warn-once-before-connect | 92 | lisp-no-bug |
| `76f5181bc6af` | Improve source NUH handling in ERC | 60 | lisp-no-bug |

### lisp/mail/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `547b1ee7b6da` | Fix Rmail behavior wrt globalized minor modes | 5 | lisp-no-bug |
| `0fb9d096e38a` | The summary scan should include the current msg and run to end. | 6 | lisp-no-bug |

### lisp/net/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `d0d657fa9027` | ; Minor Tramp cleanup | 11 | lisp-no-bug |
| `025ecf9e7b45` | * lisp/net/rcirc.el (rcirc-monospace-text): Inherit 'fixed-pitch' | 2 | lisp-no-bug |

### lisp/obsolete/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `9bf2a19bb214` | Move gnus-dbus.el to obsolete/gnus-dbus.el | 0 | missing-file:lisp/obsolete/gnus-dbus.el |
| `d54faa0f1bff` | Mark gnus-dbus.el as obsolete | 27 | missing-file:lisp/obsolete/gnus-dbus.el |

### lisp/progmodes/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `56f27dd9f066` | Eglot: fix eglot--sig-info with non-UTF-32 positionEncoding | 114 | lisp-no-bug |

### lisp/textmodes/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `fe58f45782cb` | Allow changing SGML "quick keys" after loading sgml-mode.el | 171 | lisp-no-bug |
| `7eab6ef3cee2` | Fix 'sgml-parse-tag-backward' to handle tags in comments | 8 | lisp-no-bug |

### lisp/url/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `306f4d166082` | url-cookie: use C locale when formatting expiry times | 20 | lisp-no-bug |

### lisp/vc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `07f2bbc905d8` | vc-dir-resynch-file: Pass down non-truename'd FILE | 26 | lisp-no-bug |
| `9bc04b001ac9` | vc-next-action: Call vc-delete-file on FILESET-ONLY-FILES | 2 | lisp-no-bug |

### doc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `984024daf3ce` | Gnus: Use new sleep library | 55 | missing-file:etc/NEWS |
| `e4d529c67b6a` | ; Fix last change | 27 | missing-file:etc/NEWS |
| `519fd832111c` | Fix secrets.el when Emacs is a flatpak | 46 | lisp-multi-area |
| `a8f67a1f0670` | Change ERC version for Emacs 31 to 5.6.2.31.1 | 6 | lisp-multi-area |
| `08dc13ea94f1` | Change ERC version to 5.7-git | 11 | lisp-multi-area |
| `2e71d2c709f0` | Propagate EMACSCLIENT_TRAMP to remote hosts with Tramp | 48 | lisp-multi-area |
| `aba60ad0c5be` | Eglot: prefer markdown-ts-view-mode for markup rendering (bug#80127) | 100 | lisp-multi-area |

### etc/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `cf9728c4be8f` | Only perform erc-log-insert-log-on-open setup once | 316 | missing-file:test/lisp/erc/erc-scenarios-log-options.el |
| `66729f3e5080` | New variable 'completion-frontend-properties' (bug#80990) | 53 | missing-file:etc/NEWS |
| `1613f2e65263` | Preserve order of local ERC modules for activation | 18 | lisp-multi-area |
| `ec7a5f85c934` | Run module setup in ERC query buffers on reconnect | 19 | lisp-multi-area |
| `a0c05029fd18` | * etc/NEWS: Mention new user option tramp-propagate-emacsclient-tramp. | 7 | missing-file:etc/NEWS |
| `bf89ee6d078c` | ; * etc/PROBLEMS: Cursor not shown on Windows with system caret (bug#81047). | 24 | unclassified |
| `b13450973abb` | Copy changes from tarballs when installing VC packages | 35 | missing-file:etc/NEWS |
| `84e646f0b320` | ; * etc/NEWS: Fix last change. | 12 | missing-file:etc/NEWS |

### admin/

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `cb21b7d71f4e` | Mark myself as maintainer of sgml-mode | 3 | lisp-multi-area |

### other

| SHA | Subject | Lines | Why |
|---|---|---|---|
| `4fcc8a473a19` | ; Spelling fixes. | 64 | missing-file:etc/NEWS |

## Failed (cherry-pick aborted)

| SHA | Subject | Conflict |
|---|---|---|
| `98c28606d2a6` | ; Fix typo | conflict:lisp/url/url-cookie.el |

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
| `c2a24dcec8ba` | ; update msys2 build helper for Emacs 31 & UCRT | admin |
| `13039e3442b8` | ; touch-up last commit: copyright and comments | admin |
