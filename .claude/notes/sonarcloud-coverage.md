# SonarCloud + Test Coverage

How this fork feeds C test-coverage data to SonarCloud, and why the
pipeline is shaped the way it is.

## What SonarCloud actually analyzes

SonarCloud's project (`Jylhis_emacs`, org `jylhis`) scans the **C/C++**
sources via the CFamily analyzer plus the **Python** under `meson/`.
There is **no Elisp analyzer**, so Elisp coverage cannot be displayed
even though the test suite (ERT) is mostly Elisp.  The coverage that
matters is therefore **C coverage**, which is produced as a side effect
of running the instrumented `emacs` binary through the ERT suite.

## Pipeline

Two entry points, split by event:

1. **Dev pushes -> `.github/workflows/meson.yml` job `coverage`**
   (runs when `linux_meson` is classified true):
   - `meson setup build -Db_coverage=true` (adds `--coverage`, i.e.
     `-fprofile-arcs -ftest-coverage`, to compile + link; also writes
     `build/compile_commands.json` for the CFamily analyzer).
   - Mirrors the build-and-test compile chain; foundation + dump +
     smoke suite are the **green-run gate** (no `continue-on-error`).
     The full-lisp byte-compile tail and the broad ERT suite are
     tolerated (`continue-on-error`) so the dump can fall back to `.el`
     and the broad suite widens exercised C paths without gating
     coverage.
   - `gcovr --root . --sonarqube coverage.xml --filter src/
     --filter lib-src/` converts the `.gcda`/`.gcno` data into the
     SonarQube **generic test-coverage XML** with repo-relative paths
     (only when the gate passed).
   - **Runs the SonarCloud scan in the same job** (`if: always()`), so
     the coverage report always matches the exact revision being
     scanned.  The `sonar.coverageReportPaths` define is added only
     when `hashFiles('coverage.xml')` is non-empty, so a missing report
     (failed build) never trips the generic coverage importer -- dev is
     still analyzed, just without coverage.

2. **Pull requests -> `.github/workflows/sonarcloud.yml`**:
   - `meson setup build` (no compile) + CFamily scan over
     `compile_commands.json`.  **No coverage** -- coverage is a
     dev-branch trend metric and an instrumented build per PR is too
     expensive.  Same-repo PRs only (fork PRs lack `SONAR_TOKEN`).

`sonar-project.properties` deliberately does **not** set
`sonar.coverageReportPaths`; it is passed per-run via `--define` only
when the report exists.

## Why this shape (design history)

The first cut produced the coverage artifact in meson.yml and had
sonarcloud.yml download the latest one off dev cross-workflow.  PR
review (codex) flagged two real bugs that are inherent to that split:

- A configured-but-missing report makes the generic coverage importer
  **fail the scan** (not just warn).  Hence: never set the property
  unless the file exists.
- Importing coverage from a **different revision** can fail analysis on
  out-of-range line numbers when a C file's line count changed.  And
  the long instrumented build means the same-commit artifact is never
  ready when a concurrent fast scan runs, so "latest off dev" is always
  stale.

Scanning from inside the coverage job removes both: the report is
exact-revision and guaranteed present (or cleanly absent).

## Tradeoffs / follow-ups

- **Dev analysis is now gated on the instrumented build** and delayed
  by its duration (~build length) instead of the old fast setup-only
  scan.  The scan still runs (`always()`) if the build fails, so dev is
  never left unanalyzed; it just loses coverage for that push.
- **Config-only dev pushes** (e.g. touching only
  `sonar-project.properties`) set `sonar` but not `linux_meson`, so the
  coverage job is skipped and that push is not scanned; the next code
  push re-scans.  Accepted.
- **Strictness vs. breadth**: pure "fail on any ERT failure" would mean
  coverage rarely updates given the documented flaky pdmp/byte-compile
  tail, so coverage is gated on the deterministic core (build + dump +
  smoke) while the broad suite runs best-effort for breadth.  Tighten
  once the flaky long-tail is triaged.
- `gcovr` is pinned via `devenv.nix` so CI and local shells agree.
