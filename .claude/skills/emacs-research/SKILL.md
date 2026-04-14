# Emacs Research

Research a topic, subsystem, or approach within GNU Emacs and produce a decision-ready summary.

## When to Use

Invoke with `/research` when you need to understand an Emacs subsystem, evaluate an approach, or investigate how something works before making changes.

## Process

1. **Clarify the question** — Ask for specifics if the request is unclear
2. **Search the codebase** — Use grep, find, and code reading to locate relevant implementations
3. **Search documentation** — Check Texinfo manuals (`doc/`), `etc/NEWS`, `admin/notes/`, and inline comments
4. **Search external sources** — Bug tracker (debbugs.gnu.org), emacs-devel archives, EmacsWiki
5. **Document findings** — For each option or approach, note what it is, how it works, trade-offs, and maturity

## Output Structure

- **Question**: The core inquiry
- **Findings**: What was discovered, with code references and source links
- **Recommendation**: Suggested approach with rationale
- **Sources**: File paths, bug numbers, URLs to documentation or discussions

## Emacs-Specific Research Paths

| Topic | Where to Look |
|-------|--------------|
| How a Lisp function works | `lisp/` source, `doc/lispref/` manual |
| How a C primitive works | `src/` source, DEFUN definition, `doc/lispref/` |
| Display/redisplay behavior | `src/xdisp.c`, `src/dispnew.c`, `doc/lispref/display.texi` |
| Key binding / input | `src/keyboard.c`, `src/keymap.c`, `lisp/bindings.el` |
| Package/feature history | `etc/NEWS*`, git log, debbugs.gnu.org |
| Build system | `configure.ac`, `Makefile.in`, `admin/notes/` |
| Platform-specific | `nextstep/`, `java/`, `nt/`, `msdos/` |

Keep it concise — the goal is enabling decisions, not encyclopedic coverage.
