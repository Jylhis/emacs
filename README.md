# Jotain Emacs

**Jotain Emacs** is [Jylhis](https://jylhis.com)'s fork of [GNU Emacs](https://www.gnu.org/software/emacs/) v31.0.50 (development branch).

> **License:** GPL v3 or later, inherited from GNU Emacs upstream.  See [COPYING](COPYING).

---

## What This Fork Does Differently

| Area | Upstream GNU Emacs | Jotain Emacs |
|------|--------------------|--------------|
| **Build system** | Autotools (`configure` / `make`) | **Meson + Ninja only** (autotools removed at commit `313f867`) |
| **Dev environment** | Manual setup | `devenv` + Nix flake (`devenv.nix`, `flake.nix`) |
| **Upstream sync** | Human-driven cherry-pick | AI-assisted `upstream-commit-review` skill with automated triage |
| **Supported platforms** | Many (Linux, Windows, macOS, BSDs, …) | GNU/Linux x86\_64/aarch64, macOS x86\_64/arm64, Android |
| **CI** | None in upstream tree | GitHub Actions (build, release, static analysis, security scanning) |

This is a living engineering dogfood environment: Jylhis uses Emacs as its primary development editor and feeds improvements back to the fork.

---

## Dogfood Plan

Jylhis engineers run Jotain Emacs as their daily driver.  The feedback loop is:

1. **Use** — engineers hit a rough edge in vanilla Emacs.
2. **Fix** — file an issue or directly cut a branch (`codex/` or `claude/`).
3. **Review** — run the `upstream-commit-review` skill weekly to absorb safe upstream commits.
4. **Ship** — merged fixes land on `dev`; tagged releases publish via `release.yml`.

Design system integration: the Jylhis design system emits `platforms/emacs/jylhis-{paper,roast}-theme.el` which will be consumed by this fork once the theme pipeline is stable.

---

## CI Status

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| [`meson.yml`](.github/workflows/meson.yml) | Push / PR | Build + Meson smoke tests |
| [`release.yml`](.github/workflows/release.yml) | Tag push | Staged install + release artifact |
| [`sonarcloud.yml`](.github/workflows/sonarcloud.yml) | Push | Static analysis (SonarCloud) |
| [`codeql.yml`](.github/workflows/codeql.yml) | Push / schedule | Security scanning (CodeQL) |

No `dependabot.yml` for code dependencies (upstream manages those via cherry-pick); `dependabot` is enabled for GitHub Actions version tracking only.

---

## Quick Start

```bash
# Reproducible dev shell (requires Nix + devenv)
devenv shell

# Build
meson setup build
meson compile -C build

# Smoke tests
meson test -C build --suite smoke

# Debug build
meson setup build --buildtype=debug -Dcheck=yes,glyphs -Dcheck-lisp-object-type=true

# Run without user config
./src/emacs -Q
```

---

## Repository Layout

```
src/          C source — Lisp interpreter, display, GC, bytecode VM
lisp/         Emacs Lisp — modes, packages, standard library
test/         ERT test suite
doc/          Texinfo manuals
lib/          Gnulib portability library
lib-src/      Helper executables (etags, emacsclient, …)
admin/        Release tools, developer notes
etc/          Data files, NEWS, tutorials, images
meson/        Meson helper scripts
nix/          Nix packaging, overlays, module definitions
.claude/      AI agent notes, rules, and skills
```

---

## Upstream Sync

Upstream commits are triaged with the `upstream-commit-review` skill.
As of 2026-05-31: **64 commits pending review**, 59 applied in the latest session.
AI-generated branches (`claude/`, `codex/`) are reviewed separately before merge.

See `.claude/notes/upstream-backport-review-latest.md` for the current backlog report.

---

## Contributing

This fork follows GNU Emacs conventions where applicable:

- American English, two spaces between sentences.
- Fill column 72 for code and docstrings.
- Commit format: ChangeLog style, present tense, 50-char summary.
- See [CONTRIBUTE](CONTRIBUTE) for the full upstream contributor guide.
- See [CLAUDE.md](CLAUDE.md) and [AGENTS.md](AGENTS.md) for AI-agent-specific guidance.

Bug reports for upstream issues: `bug-gnu-emacs@gnu.org` / `M-x report-emacs-bug`.
Fork-specific issues: file a Jylhis issue.
