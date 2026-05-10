#!/usr/bin/env bash
# Classify changed paths into CI work buckets.

set -euo pipefail

zero_sha=0000000000000000000000000000000000000000

event_name=${EVENT_NAME:-${GITHUB_EVENT_NAME:-}}
ref=${REF:-${GITHUB_REF:-}}
head_sha=${HEAD_SHA:-${GITHUB_SHA:-HEAD}}
base_sha=
full_validation=false

if [ -n "${CHANGED_FILES:-}" ]; then
  mapfile -t changed_files <<<"$CHANGED_FILES"
elif [ "$event_name" = "workflow_dispatch" ] || [[ "$ref" == refs/tags/* ]]; then
  full_validation=true
  changed_files=(__full_validation__)
elif [ "$event_name" = "pull_request" ]; then
  base_sha=${PR_BASE_SHA:-}
  if [ -z "$base_sha" ]; then
    echo "::error::PR_BASE_SHA is required for pull_request classification"
    exit 1
  fi
  mapfile -t changed_files < <(git diff --name-only "$base_sha" "$head_sha" --)
else
  base_sha=${EVENT_BEFORE:-}
  if [ -z "$base_sha" ] || [ "$base_sha" = "$zero_sha" ]; then
    full_validation=true
    changed_files=(__full_validation__)
  else
    mapfile -t changed_files < <(git diff --name-only "$base_sha" "$head_sha" --)
  fi
fi

actionlint=false
meson_python=false
meson_guard=false
linux_meson=false
sonar=false
codeql_actions=false
codeql_cpp=false
codeql_python=false

if [ "$full_validation" = true ]; then
  actionlint=true
  meson_python=true
  meson_guard=true
  linux_meson=true
  sonar=true
  codeql_actions=true
  codeql_cpp=true
  codeql_python=true
else
  for path in "${changed_files[@]}"; do
    case "$path" in
      .github/workflows/*.yml|.github/workflows/*.yaml)
        actionlint=true
        codeql_actions=true
        ;;
      action.yml|action.yaml|*/action.yml|*/action.yaml)
        codeql_actions=true
        ;;
    esac

    case "$path" in
      meson/*.py)
        meson_python=true
        linux_meson=true
        sonar=true
        codeql_python=true
        ;;
      *.py)
        codeql_python=true
        ;;
    esac

    case "$path" in
      lib/meson.build)
        meson_guard=true
        ;;
    esac

    case "$path" in
      .github/workflows/meson.yml|.github/scripts/check-install-parity.sh|meson.build|meson.options|*/meson.build|meson/**|src/**|lib/**|lib-src/**|lisp/**|test/**|admin/**|m4/gnulib-common.m4|m4/extern-inline.m4)
        linux_meson=true
        ;;
    esac

    case "$path" in
      .github/workflows/sonarcloud.yml|sonar-project.properties|meson.build|meson.options|*/meson.build|meson/**|src/**|lib/**|lib-src/**|m4/gnulib-common.m4|m4/extern-inline.m4|*.c|*.h|*.cc|*.cpp|*.cxx|*.hpp|*.m|*.mm)
        sonar=true
        ;;
    esac

    case "$path" in
      *.c|*.h|*.cc|*.cpp|*.cxx|*.hpp|*.m|*.mm)
        case "$path" in
          build/*) ;;
          *) codeql_cpp=true ;;
        esac
        ;;
    esac
  done
fi

macos_meson=false
if [ "$event_name" = "push" ] && [ "$ref" = "refs/heads/dev" ] && [ "$linux_meson" = true ]; then
  macos_meson=true
fi

{
  echo "Changed files:"
  printf '  %s\n' "${changed_files[@]}"
  echo "CI buckets:"
  echo "  actionlint=$actionlint"
  echo "  meson_python=$meson_python"
  echo "  meson_guard=$meson_guard"
  echo "  linux_meson=$linux_meson"
  echo "  macos_meson=$macos_meson"
  echo "  sonar=$sonar"
  echo "  codeql_actions=$codeql_actions"
  echo "  codeql_cpp=$codeql_cpp"
  echo "  codeql_python=$codeql_python"
}

output=${GITHUB_OUTPUT:-}
if [ -n "$output" ]; then
  {
    echo "actionlint=$actionlint"
    echo "meson_python=$meson_python"
    echo "meson_guard=$meson_guard"
    echo "linux_meson=$linux_meson"
    echo "macos_meson=$macos_meson"
    echo "sonar=$sonar"
    echo "codeql_actions=$codeql_actions"
    echo "codeql_cpp=$codeql_cpp"
    echo "codeql_python=$codeql_python"
  } >>"$output"
fi
