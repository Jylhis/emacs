# Research Notes

Investigative and research notes for GNU Emacs development.  These
notes capture findings from exploring the repository documentation,
build system, developer tooling, and conventions.  They serve as a
quick reference so we do not need to re-read lengthy files each
session.

## Index

- [Build System](build-system.md) -- configure options, macOS/NS
  build, debug builds, and incremental rebuild strategies.
- [Developer Tools](developer-tools.md) -- admin/ scripts, codespell,
  coccinelle, emake, bisect, and CI infrastructure.
- [Conventions and Style](conventions-and-style.md) -- spelling,
  documentation rules, commit messages, NEWS entries, and jargon.
- [Git Workflow](git-workflow.md) -- branching model, worktrees,
  merging release branches, and bisecting.
- [DevEnv Gaps](devenv-gaps.md) -- packages and scripts missing from
  devenv.nix that the upstream docs recommend.
- [Fork TODOs](fork-todos.md) -- open follow-up work for this fork
  (local ldefs-boot.el regeneration, etc.).
- [Upstream-patch work review (2026-05-21)](upstream-work-review-2026-05-21.md)
  -- consolidated retrospective of all savannah backports and Darwin
  patch absorption to date; entry point for the per-session
  `upstream-backport-review-*.md` reports.

### External Forks and Patch Sources

These notes describe Emacs forks and patch repos referenced
(directly or transitively) by `jotain/`'s Nix configuration, plus a
couple of upstream-of-jotain sources tracked for completeness.
Verdicts are written in the **absorb-into-`jylhis/emacs`** direction:
which patches should this fork carry, not which patches GNU upstream
should accept.

Per-patch verdict scale: `absorb-now`, `verify-then-absorb`, `defer`,
`not-applicable`.

- [Homebrew emacs-plus](fork-homebrew-emacs-plus.md) -- source of
  truth for the Darwin patch set (system-appearance,
  round-undecorated-frame, fix-ns-x-colors).  Two `absorb-now`
  candidates and one `verify-then-absorb`.
- [nix-giant/nix-darwin-emacs](fork-nix-darwin-emacs.md) -- Nix
  overlay that re-hosts a subset of the emacs-plus patches; verdicts
  cross-reference the emacs-plus note.
- [MacPorts](fork-macports.md) -- `editors/emacs` and
  `aqua/emacs-mac-app` ports; mostly MacPorts-specific path / launchd
  glue, mostly `defer` or `not-applicable`.
- [Emacs Mac Port](fork-emacs-mac-port.md) -- Yamamoto/jdtsmith
  alternative macOS GUI backend; not patch-shaped (parallel codebase);
  reference value only.
- [nix-community/emacs-overlay](fork-nix-emacs-overlay.md) -- Nix
  overlay with a Nix-specific native-comp patch only; nothing to
  absorb, useful as a downstream breakage canary.
- [Aquamacs](fork-aquamacs.md) -- macOS Emacs distribution;
  NSSpellChecker primitives are a notable NS-port gap (defer to a
  separate workstream).

The `.claude/skills/upstream-commit-review` skill has a "patch-source
poll" step (`attributes/patch-sources.toml`) that watches these
repos for new/changed `.patch` files and surfaces them in its
report.
