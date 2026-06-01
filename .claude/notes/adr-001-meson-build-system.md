# ADR-001: Meson + Ninja as the Sole Build System

**Status:** Accepted (fork-imposed)
**Date:** 2026-06-01
**Deciders:** Jylhis FoundingEngineer

---

## Context

GNU Emacs upstream uses Autotools (`configure.ac`, `autogen.sh`, `Makefile.in`)
as its build system.  This fork replaced Autotools with **Meson + Ninja** at
cutover commit `313f867`, removing `configure.ac`, `autogen.sh`, every
`Makefile.in`, `GNUmakefile`, and `make-dist` from the tree.

The Jylhis engineering canon has no stated preference between Autotools and
Meson; Meson was chosen by the original fork author before this ADR process
was in place.

---

## Decision

Meson + Ninja remains the **only** supported build system for Jotain Emacs.
We will not restore Autotools compatibility.

---

## Rationale

1. **Fork-imposed, not a canon violation.**  Jylhis has no policy mandating
   Autotools.  Meson is a modern build system with better IDE integration,
   faster incremental builds, and first-class cross-compilation support
   (already used for Android cross-builds in this repo).

2. **Devenv / Nix alignment.**  `devenv.nix` provides Meson, Ninja, and
   Python3 as first-class dev dependencies.  The Nix flake wraps the Meson
   build directly.  Restoring Autotools would require adding autoconf,
   automake, and libtool to the dev environment for no functional gain.

3. **Upstream delta is managed, not closed.**  Upstream uses Autotools; we
   absorb upstream commits via the `upstream-commit-review` skill and resolve
   any build-system conflicts as part of that process.  This is a known,
   bounded cost.

4. **Platform scope is narrower.**  This fork supports Linux x86\_64/aarch64,
   macOS x86\_64/arm64, and Android — not the broad portability matrix
   upstream targets.  Autotools' primary value is broad portability; Meson
   covers our target set without it.

---

## Consequences

- **Positive:** Simpler build setup, faster CI, better cross-compilation.
- **Negative:** Diverges from upstream; upstream build-system commits require
  adaptation during triage; contributors familiar with GNU Emacs must learn
  Meson.
- **Ongoing cost:** Upstream build-system patches are filtered during
  `upstream-commit-review` and applied only when they have a Meson analogue.

---

## Alternatives Considered

- **Restore Autotools** — rejected: high maintenance cost, adds no value for
  our target platform set, and breaks the existing Nix/devenv integration.
- **Dual support (Autotools + Meson)** — rejected: doubles build maintenance
  burden and was explicitly removed at `313f867` for good reason.

---

## Stack Canon Note

Meson/C/Elisp is a **fork-imposed** stack, not a Jylhis-canon stack choice.
The Jylhis engineering canon (established separately) does not prescribe
editor infrastructure stacks.  No canon waiver is required; this ADR is
recorded for transparency.
