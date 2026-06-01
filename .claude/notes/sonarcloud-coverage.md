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

1. **`.github/workflows/meson.yml` -> job `coverage`** (dev pushes only,
   when `linux_meson` classified true):
   - `meson setup build -Db_coverage=true` (adds `--coverage`, i.e.
     `-fprofile-arcs -ftest-coverage`, to compile + link).
   - Mirrors the build-and-test compile chain; foundation + dump +
     smoke suite are the **green-run gate** (no `continue-on-error`).
     The full-lisp byte-compile tail and the broad ERT suite are
     tolerated (`continue-on-error`) so the dump can fall back to `.el`
     and the broad suite widens exercised C paths without gating upload.
   - `gcovr --root "$PWD" --sonarqube coverage.xml --filter 'src/'
     --filter 'lib-src/'` converts the `.gcda`/`.gcno` data into the
     SonarQube **generic test-coverage XML** with repo-relative paths.
   - Uploads it as artifact **`coverage-sonarqube`**.
   - Dedicated job (not folded into build-and-test) because instrumented
     objects must not pollute that job's ccache, and so its strictness
     does not depend on the flaky shared build.  Once per dev push to
     bound cost.

2. **`.github/workflows/sonarcloud.yml` -> job `analyze`**:
   - A `actions/github-script` step lists recent `meson.yml` runs on
     `dev`, finds the newest `coverage-sonarqube` artifact, and unpacks
     `coverage.xml` at the repo root.  Needs `actions: read`.
   - The scan imports it via `sonar.coverageReportPaths=coverage.xml`
     (set in `sonar-project.properties`).
   - Decoupled by design: the scan does **not** wait for the coverage
     build.  It pulls the latest available report off `dev`, so coverage
     can lag the scanned commit by a push.  Missing report => scan still
     runs, just with no coverage for that run (no failure).

## Tradeoffs / follow-ups

- **Staleness**: PR scans and same-push dev scans see the *previous*
  dev push's coverage, not the exact commit.  Accepted to avoid a
  per-scan instrumented rebuild.  A `workflow_run`-triggered scan would
  make it commit-exact at the cost of losing PR context.
- **Strictness vs. breadth**: pure "fail on any ERT failure" would mean
  coverage almost never updates given the documented flaky
  pdmp/byte-compile tail, so upload is gated on the deterministic core
  (build + dump + smoke) while the broad suite runs best-effort for
  breadth.  Tighten once the flaky long-tail is triaged.
- `gcovr` is pinned via `devenv.nix` so CI and local shells agree.
