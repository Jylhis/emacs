# Library Replacement Audit

A sweep of `src/`, `lisp/`, `lib/`, and `lib-src/` for code that
reimplements functionality available in external libraries.  Goal:
identify candidates where outsourcing would reduce the in-tree code
we maintain, and rank them by effort vs. risk.

Replacement preference order (per user direction):

1. C standard library / POSIX
2. Modern, well-maintained libraries (utf8proc, libfribidi, PCRE2,
   libcurl, libgit2, libarchive, libgsasl, c-ares, …)
3. GNU project libraries (gnulib, libgmp, libnettle, GnuTLS)
4. Vendored copy in-tree

Audit performed 2026-05-25 by three parallel exploration agents.
Findings below are **candidates** -- spot-checks revealed several
mistakes in the raw agent reports (most notably the claim that
`src/json.c` uses jansson, which is the opposite of reality, see
section 4).  Every entry should be verified before acting on it.


## 0. Already outsourced (do not undo)

These are deliberate decisions to depend on (or to stop depending
on) an external library.  Reverting any of them would conflict with
Emacs project policy.

| Subsystem                | Library                       | Notes |
|--------------------------|-------------------------------|-------|
| Bignum (`src/bignum.c`)  | libgmp (mandatory)            | `src/mini-gmp*.c` is the in-tree fallback for absent systems. |
| XML parsing (HTML/XML)   | libxml2                       | `lisp/xml.el` predates libxml2 binding; it is a pure-Lisp fallback. |
| TLS (`src/gnutls.c`)     | GnuTLS                        | Hard dependency in modern builds. |
| Tree-sitter parsing      | libtree-sitter                | Replaces ad-hoc parsers in `*-ts-mode` files. |
| Font shaping             | HarfBuzz (`src/hbfont.c`)     | Used alongside (not replacing) Emacs's composition model. |
| Native compilation       | libgccjit                     | Optional but standard. |
| SQLite (`src/sqlite.c`)  | sqlite3                       | |
| Image formats            | libjpeg / libpng / libtiff /  | Already wrapped in `src/image.c`. |
|                          | giflib / libwebp / librsvg /  | |
|                          | libxpm / ImageMagick          | |
| Crypto hashes (md5/sha*) | gnulib `lib/md5.c`, `sha*.c`  | NOT linked to OpenSSL/Nettle; see §4.1. |
| JSON (`src/json.c`)      | **none** -- intentionally     | Jansson was removed in Emacs 30 (`etc/NEWS.30`). Native parser is faster and avoids a library quirk. Replacing this would be regressive. |
| Regex (etags/ebrowse)    | gnulib `lib/regex.c`          | Only on systems lacking glibc's GNU regex API. |
| Color management         | lcms2                         | Optional. |
| Audio                    | ALSA / OSS (`src/sound.c`)    | Could be widened to libcanberra; low priority. |


## 1. Top replacement candidates (high ROI, contained scope)

These are the entries the audit considers worth pursuing first.
"Effort" is rough: Trivial = days; Moderate = weeks; Major = months.

### 1.1 `lisp/arc-mode.el` (2552 lines) -> libarchive

Shells out to one CLI per format (`tar`, `unzip`, `lha`, `7za`,
`lsar`, `cabextract`, ...).  A libarchive dynamic module would
replace 8+ external tool invocations with one library handling
zip/tar/cpio/rar/7z/lha/iso uniformly.

- Effort: Moderate.  Dynamic module + thin Lisp wrapper.
- Risk: Low.  UI layer (Tar / Archive mode buffers) stays untouched.
- Verify first: which archive formats arc-mode actually exercises
  in CI, and which libarchive build options are needed.

### 1.2 `lisp/net/dns.el` (515 lines) -> c-ares or `getaddrinfo`

Hand-rolled UDP DNS resolver in Lisp.  Only used by SMTP and a few
gnus backends.  POSIX `getaddrinfo` already covers the A/AAAA cases
via Emacs core; c-ares would cover MX / SRV / async.

- Effort: Trivial.
- Risk: Low; replacement is opt-in.

### 1.3 `lisp/net/sasl*.el` (~770 lines) + `lisp/net/ntlm.el` (714 lines) -> libgsasl

Multiple SASL mechanisms (CRAM-MD5, DIGEST-MD5, SCRAM-SHA-256, NTLM)
implemented in pure Lisp, with their own MD4/HMAC/MD5 primitives
(`lisp/md4.el`, `lisp/hex-util.el`).  Replacing with libgsasl via a
module eliminates ~1.5k lines of crypto-in-Lisp.

- Effort: Trivial wrapper, Moderate validation.
- Risk: Auth code -- needs careful test coverage across IMAP/SMTP/
  pop3.

### 1.4 `lib-src/etags.c` (217k of binary; ~7k of source) -> universal-ctags

universal-ctags has supported emacs-etags output (`-e`,
`--output-format=u-ctags`) for years and covers far more languages.
The migration is not "drop etags" but "ship a thin wrapper or
recommend universal-ctags as the default in docs."

- Effort: Moderate (wrapper + NEWS/doc); Major if we remove etags.
- Risk: Decades of muscle memory and `tags-table-list` setups.
  Suggest soft deprecation, not removal.

### 1.5 `lib-src/rcs2log` -> remove

Shell script that converts RCS logs to ChangeLog.  RCS is effectively
extinct; users on modern VCSes do not need this.

- Effort: Trivial (`git rm`, NEWS entry).
- Risk: None we can foresee.  Confirm via emacs-devel before removal.

### 1.6 Crypto: optionally link `libnettle` (or OpenSSL) for hashes

`lib/md5.c`, `lib/sha*.c`, `lib/sha3.c` are gnulib's portable
implementations.  None of them is hooked up to libcrypto / Nettle.
On modern Linux/macOS, system libraries provide CPU-accelerated
implementations (SHA-NI, AES-NI) that beat gnulib measurably.

- Effort: Moderate (probe + conditional dispatch in `src/fns.c`'s
  `secure-hash`).
- Risk: Build-system delta, ABI variance between OpenSSL 1.1/3.0,
  LibreSSL, Nettle.  Keep gnulib path as fallback.


## 2. Mid-tier candidates (worth scoping)

### 2.1 `src/regex-emacs.c` (5338 lines) -> PCRE2 or oniguruma

Emacs's regex engine is tightly bound to syntax tables, character
categories, and the buffer object model.  A drop-in replacement is
not feasible; an embedded variant (PCRE2 with custom hooks for
syntax-table lookup) might be.

- Effort: Major.  Treat as a research project, not a sprint.
- Risk: High.  Performance regression risk in core text operations;
  semantics differ around bound assertions, look-ahead, etc.

### 2.2 `src/bidi.c` (3724 lines) -> libfribidi

libfribidi implements UAX#9 and is widely used.  Emacs's iterator
model (one character at a time) does not match libfribidi's
paragraph-at-a-time API; a stateful adapter would be required.

- Effort: Major.
- Risk: High -- display engine is the hottest path in Emacs.

### 2.3 Unicode case mapping & properties (~2k lines)

`src/casefiddle.c`, `src/casetab.c`, `src/character.c`,
`src/charset.c` carry their own Unicode tables built from
`admin/unidata/`.  utf8proc (small, MIT, ~10k LoC total) or
libunistring (GNU) could provide the same data.

- Effort: Moderate.
- Risk: Buffer-local case tables (an Emacs-specific feature) need
  a wrapper layer; libraries assume global Unicode rules.

### 2.4 `lib-src/ebrowse.c` (96k binary) -> LSP / clangd

C++ class browser, predates LSP.  Modern C++ users prefer
`lsp-mode`/`eglot` + clangd.  Could be soft-deprecated.

- Effort: Trivial to deprecate, Major to fully retire (migration
  guide, tooling glue).
- Risk: Low; user base is small.

### 2.5 `lisp/vc/vc-git.el` (~3k lines) -> libgit2 module

Currently shells out to `git` for every operation; a libgit2-backed
module could batch operations and avoid process-spawn overhead in
large repos.  vc.el's backend dispatch keeps the existing path
working in parallel.

- Effort: Moderate.
- Risk: libgit2 API churn between major versions; ship as opt-in.

### 2.6 Mode replacements via tree-sitter

`*-ts-mode` already exists for many languages.  Candidates to
deprecate or alias:
- `lisp/textmodes/sgml-mode.el` (2716 lines) -> `html-ts-mode`
- `lisp/textmodes/css-mode.el` (2203 lines) -> `css-ts-mode`
  (grammar exists upstream)
- `lisp/textmodes/tex-mode.el` (4189 lines) -> `latex-ts-mode`
  (grammar maturity needs verification first)
- `lisp/cedet/semantic/*` (~3k lines) -> tree-sitter + LSP

- Effort: Trivial to alias, Moderate to migrate user-facing keymaps.
- Risk: Workflow churn.  Discuss on emacs-devel before flipping
  defaults.


## 3. Low-priority / not worth pursuing

- `src/sfnt.c` (21k lines, TrueType parser): FreeType already linked,
  but `sfnt.c` exists specifically to support builds without
  FreeType (Android, minimal X).  Replacing means hard-requiring
  FreeType everywhere.  Defer.
- `src/coding.c` (12k lines, character coding): libiconv could cover
  the modern subset, but `emacs-mule`/ISO-2022-with-extensions can't
  be cleanly delegated.  Defer until we agree to drop legacy codings.
- `src/alloc.c` (custom GC): Emacs-specific; Boehm GC is not a fit.
  Not a candidate.
- `lisp/calc/` (55k lines): self-contained, already uses core bignum.
  No external CAS provides parity.
- `lisp/eshell/` (16k lines): value is the Emacs integration, not
  the shell.  Not a candidate.
- `lisp/erc/` (31k lines): mature, low maintenance burden.  Keep.
- `lisp/gnus/` (120k lines): foundational; partial delegation to
  notmuch/mu/isync is already user-side.  Wholesale replacement is
  not on the table.
- `lib/regex.c`: only compiled when system lacks glibc's GNU regex;
  needed by etags/ebrowse.  Keep as conditional.


## 4. Corrections to the raw audit (read before acting)

The parallel agents made several mistakes that would be embarrassing
to act on without verification:

### 4.1 `src/json.c` does NOT use jansson

The C agent claimed `src/json.c` is "a custom in-tree implementation
*not* using jansson" and recommended outsourcing it back to libjansson.
This is doubly wrong:

- It is indeed in-tree, but
- `etc/NEWS.30` documents: *"Native JSON support is now always
  available; libjansson is no longer used.  No external library is
  required.  The '--with-json' configure option has been removed."*

The migration was **away from** jansson because the hand-written
parser is faster and has cleaner semantics.  Do not recommend
reversing it.

### 4.2 `lisp/json.el` and `lisp/xml.el` are not "fallback only"

The Lisp agent flagged both as "already deprecated, fallback only".
Verification:

- `lisp/json.el` has individual `define-obsolete-function-alias`
  entries for a few helpers (since 28.1), but the file as a whole is
  not obsolete and is still required by some packages.
- `lisp/xml.el` has no obsolescence markers at all.

Both can probably be slimmed, but neither is a "delete this file"
candidate today.

### 4.3 `lisp/net/imap.el` is not orphaned

The Lisp agent recommended deleting `lisp/net/imap.el` on the
grounds that gnus uses `lisp/gnus/nnimap.el`.  But
`lisp/gnus/mail-source.el` still `(require 'imap)`.  At minimum, the
dependency must be untangled before removal.

### 4.4 Crypto hash "redundancy"

The lib-src agent noted that `src/md5.c` etc. duplicate `lib/md5.c`.
Spot-check shows the `src/` paths the agent referenced are the
gnulib copies under `lib/`; there is no `src/md5.c`/`src/sha*.c`
duplication.  Only one copy exists.


## 5. Suggested next steps

In priority order:

1. **Confirm scope with maintainer / emacs-devel.**  Several of the
   replacements above touch externally-visible APIs (`vc-git`, `etags`
   defaults, `arc-mode`).  These need community buy-in before code
   work begins.
2. **Pick one contained win to prototype first.**  Recommended:
   `lisp/net/dns.el` -> c-ares module.  Smallest blast radius, clear
   wins, exercises the dynamic-module path.
3. **Library detection in `meson.options`.**  Before any of the
   §1 candidates, decide whether the new dep is required or
   `auto`.  Required deps simplify code; `auto` keeps current
   portability story.
4. **Re-verify every claim in §1-2 against the actual source.**  The
   line counts and "Trivial / Moderate" labels above came from
   sub-agents that made the mistakes documented in §4.  Each entry
   needs a 30-minute sanity check before serious work.
5. **Document the OpenSSL non-integration** (see §1.6) regardless of
   whether we add it -- users in FIPS contexts need to know.


## 6. Out of scope for this audit

- `src/xdisp.c` and the display engine generally.
- `src/pdumper.c` / `src/comp.c` (portable dumper, native comp).
- Anything inside `nextstep/`, `nt/`, `java/`, `exec/` -- platform
  ports with their own design constraints.
- Documentation packages (`doc/`, `info/`).
- Tests under `test/`.

These were not surveyed; if "everything" is intended, a follow-up
pass is needed.
