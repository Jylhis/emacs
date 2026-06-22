# Fork TODOs

Open follow-up work specific to this fork that isn't tracked in the
upstream bug tracker.  Add an entry whenever a decision during
upstream-commit-review (or any other session) creates downstream
intent that needs to outlive the conversation.

## Tooling

- **Local fetching of externally maintained packages.**  Several
  packages bundled under `lisp/` (e.g. `lisp/emacs-lisp/timeout.el`,
  `lisp/emacs-lisp/transient.el`, `lisp/emacs-lisp/eldoc.el`, the
  Tramp tree, Org, Eglot, ERC, Gnus, etc.) are mirrored from their
  own upstream repositories.  Upstream Emacs has periodic merges and
  ad-hoc "Update <pkg> to <version>" commits; we currently absorb
  these only by cherry-picking such commits during
  upstream-commit-review.  We want a fork-local mechanism — likely a
  manifest in `admin/` plus a `just` recipe — that pulls a given
  package from its real upstream, regenerates the in-tree copy, and
  produces a commit with the upstream SHA recorded, so we don't
  depend on GNU-Emacs cadence.  Reference: `admin/MAINTAINERS`
  "Externally maintained packages" section.
