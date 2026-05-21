# MacPorts emacs ports

MacPorts ships GNU Emacs through two top-level ports:

- `editors/emacs` — the main port, with subports `emacs`, `emacs-devel`,
  `emacs-app`, `emacs-app-devel`.  Mainline GNU Emacs source.
- `aqua/emacs-mac-app` — the Yamamoto Mitsuharu Mac port packaged as
  a macOS `.app` bundle.  Tracks `bitbucket.org/mituharu/emacs-mac`.

Not currently wired into `jotain/`'s Nix derivation, but tracked here
so the upstream-commit-review patch-source poll catches any new
MacPorts-only patches that might be worth absorbing.

## Repository

- https://github.com/macports/macports-ports
- Portfile + patches per port at
  `editors/emacs/files/*.{patch,diff}` and
  `aqua/emacs-mac-app/files/*.{patch,diff}`.
- Maintained by Dan Ports (@drkp) and others; daily activity.

## `editors/emacs` patches (as of 2026-05-20)

| File | Purpose | Verdict for `jylhis/emacs` |
|---|---|---|
| `patch-Info.plist.in.diff` | Injects `LSEnvironment.PATH = @PATH@` into the macOS app bundle plist so GUI Emacs sees MacPorts' `${prefix}/bin` in `PATH` | **defer** |
| `patch-allow-powerpc.diff` | Removes the `unported=yes` check for ancient Darwin/PowerPC builds in `configure.ac` | **not-applicable** |
| `patch-src_dbusbind.c.diff` | Removes the `XD_SIGNAL2 ("No connection to bus")` guard in `XD_DBUS_VALIDATE_BUS_NAME` so MacPorts' launchd-autolaunched dbus works without an env var | **defer** |
| `patch-tree-sitter-0.26.diff` | Renames `:eq?`/`:match?`/`:pred?` back to `:equal`/`:match`/`:pred` for tree-sitter 0.26 | **not-applicable** |

### Detail

- **`patch-Info.plist.in.diff` (defer)** — MacPorts-specific path
  injection.  Useful pattern (build-time `@PATH@` substitution into
  the app bundle plist), but the value substituted is MacPorts'
  `${prefix}/bin`.  For absorption we'd want a Meson option that
  configures the LSEnvironment block to a list supplied at configure
  time; out of scope for the survey, file under `fork-todos.md` if
  the demand appears.

- **`patch-allow-powerpc.diff` (not-applicable)** — removes the
  `unported=yes` check for `*-apple-darwin[0-9].*` in `configure.ac`.
  This branch's `configure.ac` is gone since commit `313f867` (Meson
  cutover); even if it weren't, PowerPC Darwin is not a target for
  `jylhis/emacs`.

- **`patch-src_dbusbind.c.diff` (defer)** — disables a runtime
  no-autolaunch guard.  Only matters on macOS where dbus is provided
  by MacPorts via launchd; on Nix-built Emacs we don't ship dbus on
  macOS at all (`withDbus ? pkgs.stdenv.hostPlatform.isLinux` in
  `jotain/emacs.nix`).  Re-evaluate if `jotain` ever enables dbus on
  Darwin.

- **`patch-tree-sitter-0.26.diff` (not-applicable)** — this fork's
  `doc/lispref/parsing.texi` already uses the new `:eq?`/`:match?`/
  `:pred?` predicate spellings (verified: L1476, L1485, L1487, …).
  MacPorts is backporting for older Emacs trees that still spell them
  the old way.

`editors/emacs/files/site-start-app.el` is a runtime site-start file,
not a source patch — ignored by the patch poll.

## `aqua/emacs-mac-app` patches (as of 2026-05-20)

This port targets the Yamamoto Mac port (`mituharu/emacs-mac`), not
GNU Emacs.  Its patches assume `HAVE_MACGUI` is defined and modify
`src/frame.c`, `lisp/server.el`, etc. with that assumption baked in.

| File | Purpose | Verdict for `jylhis/emacs` |
|---|---|---|
| `emacs-mac-app-multi-tty.patch` | George D. Plymale II's multi-tty patch for the Yamamoto port | **not-applicable** |
| `emacs-mac-app-devel-multi-tty.patch` | Same as above, targeting the devel branch | **not-applicable** |
| `patch-src_emacs.c.diff` | Injects `${prefix}/bin` into `PATH` at Emacs startup for the imaxima workflow | **not-applicable** |

The multi-tty patches are not portable to the NS port — they remove
explicit `(eq window-system 'mac)` checks and `HAVE_MACGUI`-gated
branches in `src/frame.c` that exist in the Yamamoto port but not in
GNU Emacs.

`patch-src_emacs.c.diff` is a `__PREFIX__` placeholder substitution
into `main()` — MacPorts-specific, and a runtime PATH manipulation that
doesn't fit the source.

`aqua/emacs-mac-app/files/site-start.el` is a runtime site-start file,
not a source patch — ignored by the patch poll.

## Polling

Tracked by `.claude/skills/upstream-commit-review`'s patch-source poll
step under two names:

- `macports-emacs` — glob `editors/emacs/files/*.patch
  editors/emacs/files/*.diff`
- `macports-emacs-mac-app` — glob `aqua/emacs-mac-app/files/*.patch
  aqua/emacs-mac-app/files/*.diff`

Both feed into the same report.  Aqua/emacs-mac-app patches are
tracked for completeness; expect everything to land with verdict
`not-applicable` unless this fork ever adopts the Yamamoto Mac port
architecture.
