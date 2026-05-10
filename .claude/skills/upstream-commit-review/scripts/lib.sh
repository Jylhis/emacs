# Shared helpers for upstream-commit-review scripts.  Sourced from
# apply.sh; not meant to be executed directly.
#
# Conventions:
# - Functions echo to stderr for human-readable progress; return 0/1
#   for success/failure.  TSV results go to files in /tmp.
# - Variables exported here are read by classify.py and report.py.

# Skill directory (path of the directory containing this lib.sh)
SKILL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SKILL_NAME=upstream-commit-review

# Repo root and remote we expect.
REPO_ROOT=$(git rev-parse --show-toplevel)
EMACS_UPSTREAM=https://git.savannah.gnu.org/git/emacs.git
REMOTE_NAME=emacs-upstream

# Output files used across scripts.
RUN_TS=$(date -u +%Y-%m-%dT%H%M)
RUN_DIR=$(mktemp -d "/tmp/${SKILL_NAME}-${RUN_TS}-XXXX")
APPLIED_TSV=${RUN_DIR}/applied.tsv
RETRY_TSV=${RUN_DIR}/retry-applied.tsv
FAILED_TSV=${RUN_DIR}/failed.tsv
NEWS_PORT_TSV=${RUN_DIR}/news-port.tsv
LOG=${RUN_DIR}/run.log
: > "$APPLIED_TSV" "$RETRY_TSV" "$FAILED_TSV" "$NEWS_PORT_TSV" "$LOG"

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$LOG" >&2; }
die() { log "FATAL: $*"; exit 1; }

# Pre-flight: working tree must be clean ignoring known harness
# directories; HEAD must not be detached.
preflight_clean() {
    local dirty
    dirty=$(git status --porcelain \
            | grep -Ev '^\?\? (\.claude/|\.direnv/|build[^/]*/|node_modules/)' \
            || true)
    [ -z "$dirty" ] || die "working tree has user changes:\n$dirty"
    git symbolic-ref -q HEAD >/dev/null || die "HEAD is detached"
}

# Pre-flight: ensure the upstream remote points at savannah.
preflight_remote() {
    local url
    if url=$(git remote get-url "$REMOTE_NAME" 2>/dev/null); then
        [ "$url" = "$EMACS_UPSTREAM" ] || \
            die "$REMOTE_NAME points at $url, expected $EMACS_UPSTREAM"
    else
        log "adding $REMOTE_NAME -> $EMACS_UPSTREAM"
        git remote add "$REMOTE_NAME" "$EMACS_UPSTREAM"
    fi
    git fetch "$REMOTE_NAME" master >/dev/null \
        || die "fetch from $REMOTE_NAME failed"
}

# Register the mergiraf merge driver and link our gitattributes into
# .git/info/attributes so it is active for this repo without polluting
# the tracked tree.
preflight_mergiraf() {
    if ! command -v mergiraf >/dev/null 2>&1; then
        log "mergiraf not on PATH; .c/.h conflicts will fall back to text merge"
        return 0
    fi
    git config --local merge.mergiraf.name "mergiraf syntax-aware merge driver"
    git config --local merge.mergiraf.driver \
        'mergiraf merge --git %O %A %B -s %S -x %X -y %Y -p %P'
    local target=${REPO_ROOT}/.git/info/attributes
    local source=${SKILL_DIR}/attributes/gitattributes
    mkdir -p "$(dirname "$target")"
    if [ ! -L "$target" ] && [ ! -e "$target" ]; then
        ln -s "$source" "$target"
    elif [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
        : # already linked
    else
        # Existing file; append our rules if they aren't already there.
        if ! grep -q '^\*\.c[[:space:]]\+merge=mergiraf' "$target"; then
            cat "$source" >> "$target"
            log "appended mergiraf rules to $target"
        fi
    fi
}

# Compute and export anchor / range metadata.
compute_range() {
    ANCHOR=$(git merge-base HEAD "$REMOTE_NAME"/master)
    ANCHOR_DATE=$(git show -s --format=%ci "$ANCHOR")
    BEHIND=$(git rev-list --count "$ANCHOR".."$REMOTE_NAME"/master)
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    export ANCHOR ANCHOR_DATE BEHIND BRANCH
}

# Materialize the trailer-set: SHAs already cherry-picked into HEAD,
# extracted from `cherry picked from commit ...` lines in commit
# messages since ANCHOR.  This catches commits whose patch-id diverged
# from upstream (e.g. resolved with -X theirs) and would otherwise leak
# through `git log --cherry-pick --right-only`.
trailer_set() {
    local out=${RUN_DIR}/trailer-set.txt
    git log --format='%(trailers:key=cherry-picked-from,valueonly,unfold)%n%B' \
            "$ANCHOR"..HEAD \
        | sed -nE \
            -e 's/^[[:space:]]*([0-9a-f]{40})[[:space:]]*$/\1/p' \
            -e 's/.*cherry picked from commit ([0-9a-f]{40}).*/\1/p' \
        | sort -u >"$out"
    printf '%s\n' "$out"
}
