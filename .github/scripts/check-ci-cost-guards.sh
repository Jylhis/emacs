#!/usr/bin/env bash
# Verify the CI workflow cost guards that keep expensive jobs scoped.

set -euo pipefail

status=0

fail() {
  local file=$1
  local message=$2
  echo "::error file=$file::$message"
  status=1
}

require_contains() {
  local file=$1
  local needle=$2
  local message=$3
  if ! grep -Fq -- "$needle" "$file"; then
    fail "$file" "$message"
  fi
}

require_any_contains() {
  local file=$1
  local needle_a=$2
  local needle_b=$3
  local message=$4
  if ! grep -Fq -- "$needle_a" "$file" \
     && ! grep -Fq -- "$needle_b" "$file"; then
    fail "$file" "$message"
  fi
}

forbid_contains() {
  local file=$1
  local needle=$2
  local message=$3
  if grep -Fq -- "$needle" "$file"; then
    fail "$file" "$message"
  fi
}

require_count_at_least() {
  local file=$1
  local needle=$2
  local min_count=$3
  local message=$4
  local count
  count=$(grep -F -c -- "$needle" "$file" || true)
  if [ "$count" -lt "$min_count" ]; then
    fail "$file" "$message"
  fi
}

meson=.github/workflows/meson.yml
codeql=.github/workflows/codeql.yml
release=.github/workflows/release.yml
sonar=.github/workflows/sonarcloud.yml

for workflow in "$meson" "$codeql" "$release" "$sonar"; do
  require_contains "$workflow" \
    "group: \${{ github.workflow }}-\${{ github.ref }}" \
    "workflow should use standard per-workflow/per-ref concurrency"
  require_contains "$workflow" \
    "cancel-in-progress: true" \
    "workflow should cancel stale in-progress runs"
done

for workflow in "$meson" "$codeql" "$sonar"; do
  require_any_contains "$workflow" "paths:" "paths-ignore:" \
    "push and pull_request triggers should be path-scoped"
  require_contains "$workflow" "doc/**" \
    "docs-only edits should not trigger heavy jobs"
  require_contains "$workflow" "'**/*.md'" \
    "markdown-only edits should not trigger heavy jobs"
done

forbid_contains "$meson" "feature/*" \
  "meson workflow should not fan out on feature-branch pushes"
forbid_contains "$meson" "fix/*" \
  "meson workflow should not fan out on fix-branch pushes"
forbid_contains "$meson" "    tags:" \
  "meson workflow should leave tag builds to release.yml"
require_count_at_least "$meson" \
  "github.event.pull_request.draft == false" 2 \
  "heavy meson jobs should skip draft pull requests"
require_contains "$meson" ".github/scripts/check-ci-cost-guards.sh" \
  "meson workflow should self-check its CI cost guards"

require_count_at_least "$codeql" \
  "github.event.pull_request.draft == false" 3 \
  "all CodeQL analyze jobs should skip draft pull requests"

require_count_at_least "$sonar" \
  "github.event.pull_request.draft == false" 1 \
  "SonarCloud analysis should skip draft pull requests"

require_contains "$release" \
  "docs-only edits cannot trigger this workflow" \
  "release workflow should document why path filters are unnecessary"
forbid_contains "$release" "    branches:" \
  "release workflow should remain tag/manual only"

exit "$status"
