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
build=false
nix=false
sonar=false
codeql_actions=false
codeql_cpp=false
codeql_python=false

if [ "$full_validation" = true ]; then
  actionlint=true
  build=true
  nix=true
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
      *.py)
        codeql_python=true
        ;;
    esac

    case "$path" in
      .github/workflows/build.yml|configure.ac|autogen.sh|Makefile.in|*/Makefile.in|m4/**|build-aux/**|src/**|lib/**|lib-src/**|lisp/**|leim/**|test/**|admin/**)
        build=true
        ;;
    esac

    case "$path" in
      flake.nix|flake.lock|default.nix|nix/**|devenv.nix|devenv.yaml|devenv.lock|.github/actions/setup-devenv/**)
        nix=true
        ;;
    esac

    case "$path" in
      .github/workflows/sonarcloud.yml|sonar-project.properties|configure.ac|src/**|lib/**|lib-src/**|*.c|*.h|*.cc|*.cpp|*.cxx|*.hpp|*.m|*.mm)
        sonar=true
        ;;
    esac

    case "$path" in
      *.c|*.h|*.cc|*.cpp|*.cxx|*.hpp|*.m|*.mm)
        codeql_cpp=true
        ;;
    esac
  done
fi

{
  echo "Changed files:"
  printf '  %s\n' "${changed_files[@]}"
  echo "CI buckets:"
  echo "  actionlint=$actionlint"
  echo "  build=$build"
  echo "  nix=$nix"
  echo "  sonar=$sonar"
  echo "  codeql_actions=$codeql_actions"
  echo "  codeql_cpp=$codeql_cpp"
  echo "  codeql_python=$codeql_python"
}

output=${GITHUB_OUTPUT:-}
if [ -n "$output" ]; then
  {
    echo "actionlint=$actionlint"
    echo "build=$build"
    echo "nix=$nix"
    echo "sonar=$sonar"
    echo "codeql_actions=$codeql_actions"
    echo "codeql_cpp=$codeql_cpp"
    echo "codeql_python=$codeql_python"
  } >>"$output"
fi
