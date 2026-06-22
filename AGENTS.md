# AGENTS.md — Jotain Emacs

Guidance for AI coding agents (Claude, Codex, etc.) working in this repository.

## What This Repository Is

A Jylhis-owned fork of GNU Emacs v31.0.50.  The only supported build system is **Meson + Ninja** (autotools was removed at `313f867`).  See [README.md](README.md) for the full project overview.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude Code–specific guidance (build, test, conventions) |
| `README.md` | Fork overview, dogfood plan, CI status |
| `devenv.nix` | Reproducible dev environment (Nix + devenv) |
| `meson.build` | Top-level build definition |
| `.claude/notes/` | Research notes, upstream-review reports, fork TODOs |
| `.claude/rules/` | Path-specific coding rules enforced by Claude Code |
| `.github/workflows/` | CI pipelines |

## Build

```bash
# Reproducible shell (recommended)
devenv shell

# Configure + build
meson setup build
meson compile -C build

# Debug build (for C work)
meson setup build --buildtype=debug \
  -Dcheck=yes,glyphs -Dcheck-lisp-object-type=true

# Full install to staging dir
meson install -C build --destdir=/tmp/stage
```

## Test

```bash
meson test -C build --suite smoke   # fast smoke set
meson test -C build                 # full suite
meson test -C build NAME            # single test by name
```

Run the smallest test that proves a change.  Do not default to the full suite for a one-line Elisp fix.

## Code Conventions

- **C source (`src/`):** GNU style, hard tabs, tab-width 8.
- **Elisp (`lisp/`):** spaces only, `lexical-binding: t`, fill column 72.
- **Commit messages:** ChangeLog format, present tense, ≤50-char summary line (no trailing period), blank second line, `(Bug#NNNNN)` for upstream bugs.
- American English throughout; two spaces between sentences.
- Do NOT add `Signed-off-by:` lines — commit hooks reject them.

## Upstream Sync Workflow

Use the `upstream-commit-review` skill to triage upstream GNU Emacs commits.  Do not cherry-pick upstream commits manually without running triage first.

Pending backlog (as of 2026-05-31): 64 commits in `needs-review` bucket.
See `.claude/notes/upstream-backport-review-latest.md`.

## AI Branch Conventions

- Branch prefix `claude/` — Claude-authored feature or fix branches.
- Branch prefix `codex/` — Codex-authored branches (often security or style fixes).
- All AI branches require human or agent review before merge to `dev`.
- Security-relevant `codex/` branches require explicit security review before merge.

## Fork-Specific TODOs

Two open tooling gaps tracked in `.claude/notes/fork-todos.md`:

1. **`ldefs-boot.el` Meson target** — need a Meson/just recipe to regenerate this autoloaded file from the current `lisp/` tree (see sub-issue filed from JYL-28).
2. **External package manifest** — need an `admin/` manifest + fetch recipe with SHA recording for externally maintained packages (Tramp, Org, Eglot, ERC, etc.) (see sub-issue filed from JYL-28).

## What Agents Should NOT Do

- Do not commit secrets, credentials, or customer data.
- Do not bypass pre-commit hooks (`--no-verify`).
- Do not cherry-pick upstream commits without running the triage skill.
- Do not merge `codex/` security-fix branches without a security review.
- Do not install new company-wide skills or grant permissions as part of code changes.
- Do not edit `LICENSE` / `COPYING` — it stays GPL v3, inherited from upstream.
