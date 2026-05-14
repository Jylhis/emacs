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
- [Lisp Runtime Internals](lisp-runtime-internals.md) -- Lisp_Object
  tagging, the seven primitives, evaluator, cons allocator, interval
  tree, and bytecode VM, with file:line landmarks.

### External Forks and Patch Sources

- [Emacs Mac Port](fork-emacs-mac-port.md) -- Yamamoto/jdtsmith
  alternative macOS GUI backend; not cherry-pickable (parallel
  architecture), useful as reference for NS port improvements.
- [nix-giant/nix-darwin-emacs](fork-nix-darwin-emacs.md) -- Nix
  overlay with 3 macOS patches (system-appearance, round-undecorated,
  ns-init-colors); system-appearance patch is high-value candidate.
- [nix-community/emacs-overlay](fork-nix-emacs-overlay.md) -- Nix
  overlay with Nix-specific native-comp patch only; useful as
  downstream breakage canary, no upstream-applicable patches.
- [Aquamacs](fork-aquamacs.md) -- macOS Emacs distribution;
  NSSpellChecker integration (11 C primitives) is notable gap
  in upstream NS port; most value is in Elisp overlay.
