#!/usr/bin/env bash
# Triage upstream candidates and apply AUTO buckets via cherry-pick.
# See SKILL.md for rule semantics; references/conflict-resolution.md
# for the retry policy.
#
# Usage:
#   bash scripts/apply.sh [--dry-run] [--smoke]
#                         [--retry-allow=PATH,PATH,...]
#
# --dry-run    print the classification TSV; do not cherry-pick.
# --smoke      after the batch, run `meson test -C build --suite smoke`.
# --retry-allow override the tier-3 drift allowlist (defaults below).

set -uo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
. "${SCRIPT_DIR}/lib.sh"

DRY_RUN=0
SMOKE=0
RETRY_ALLOW="src/keyboard.c,src/xdisp.c,src/coding.c,etc/AUTHORS"
for arg in "$@"; do
    case $arg in
        --dry-run)              DRY_RUN=1 ;;
        --smoke)                SMOKE=1 ;;
        --retry-allow=*)        RETRY_ALLOW=${arg#--retry-allow=} ;;
        -h|--help)
            sed -n '/^# Usage:/,/^[^#]/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) die "unknown arg: $arg" ;;
    esac
done

# ---- Pre-flight -------------------------------------------------------------

preflight_clean
preflight_remote
preflight_mergiraf
compute_range
TRAILER_SET=$(trailer_set)
log "anchor=${ANCHOR:0:12}  behind=${BEHIND}  trailer-set=$(wc -l <"$TRAILER_SET" | tr -d ' ')"

# ---- Classify ---------------------------------------------------------------

CLASSIFY_TSV=${RUN_DIR}/classify.tsv
python3 "${SCRIPT_DIR}/classify.py" \
    --compute-range \
    --remote-ref "${REMOTE_NAME}/master" \
    --trailer-set "${TRAILER_SET}" \
    > "${CLASSIFY_TSV}"
log "classified: $(wc -l <"$CLASSIFY_TSV" | tr -d ' ') candidates"

if [ "$DRY_RUN" -eq 1 ]; then
    cat "$CLASSIFY_TSV"
    log "dry run: stopping before cherry-pick"
    printf '%s\n' "${RUN_DIR}"
    exit 0
fi

# ---- Cherry-pick loop -------------------------------------------------------

# Helper: "is the conflict set a subset of the allowlist?"
conflicts_in_allowlist() {
    local allow=$1 conflicted=$2
    [ -n "$conflicted" ] || return 1
    local f
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        case ",${allow}," in
            *",${f},"*) ;;
            *)          return 1 ;;
        esac
    done <<< "$conflicted"
    return 0
}

# Helper: detect mergiraf engagement in a just-committed cherry-pick
# by looking at HEAD's notes (mergiraf records a `mergiraf-merged`
# attribute on resolved files via tree object trailers).  We approximate
# by checking whether any conflict-marker artefact is present.
mergiraf_resolved_files() {
    git diff --name-only "$1"~..."$1" -- '*.c' '*.h' '*.cc' '*.cpp' \
        '*.hh' '*.hpp' 2>/dev/null
}

while IFS=$'\t' read -r SHA BUCKET REASON LINES FILES; do
    [ -z "$SHA" ] && continue
    case "$BUCKET" in
        autotools|merge-noise|admin|review)
            continue ;;
        doc-only|test-only|lisp-bugfix|lisp-doc-style|small-src|lisp+news-bug)
            ;;
        *)
            log "unknown bucket '$BUCKET' for $SHA, skipping"
            continue ;;
    esac

    SUBJ=$(git show -s --format=%s "$SHA")
    SHORT=${SHA:0:12}
    log "[$BUCKET] $SHORT $SUBJ"

    if git cherry-pick -x "$SHA" >>"$LOG" 2>&1; then
        NEW=$(git rev-parse --short=12 HEAD)
        # Check whether a C/C++ file was conflict-marker-free thanks
        # to mergiraf (heuristic: if any *.c/*.h was in the commit,
        # tag with +mergiraf so the report can show range-diffs).
        if echo "$FILES" | grep -Eq '\.(c|h|cc|cpp|hh|hpp)\b'; then
            BUCKET_TAG="${BUCKET}+mergiraf?"
        else
            BUCKET_TAG="${BUCKET}"
        fi
        printf '%s\t%s\t%s\t%s\n' \
            "$SHORT" "$NEW" "$SUBJ" "$BUCKET_TAG" >> "$APPLIED_TSV"
        continue
    fi

    # Conflict.  Compute conflicted paths once for retry decisions.
    CONFLICTED=$(git diff --name-only --diff-filter=U)

    # ---- Tier 2: NEWS.31 redirect --------------------------------------
    if [ "$CONFLICTED" = "etc/NEWS.31" ]; then
        # Check upstream commit touched etc/NEWS.
        UPSTREAM_FILES=$(git show --name-only --format= "$SHA" | sed '/^$/d')
        if echo "$UPSTREAM_FILES" | grep -qx "etc/NEWS"; then
            log "  tier-2 NEWS.31 redirect"
            git cherry-pick --abort >>"$LOG" 2>&1 || true
            if git cherry-pick -x -X theirs "$SHA" >>"$LOG" 2>&1; then
                NEW=$(git rev-parse --short=12 HEAD)
                printf '%s\t%s\t%s\t%s\n' \
                    "$SHORT" "$NEW" "$SUBJ" "${BUCKET}+theirs" \
                    >> "$RETRY_TSV"
                printf '%s\t%s\n' "$SHORT" "$SUBJ" >> "$NEWS_PORT_TSV"
                continue
            fi
        fi
    fi

    # ---- Tier 3: bounded -X theirs retry -------------------------------
    if conflicts_in_allowlist "$RETRY_ALLOW" "$CONFLICTED"; then
        log "  tier-3 -X theirs (allowlist)"
        git cherry-pick --abort >>"$LOG" 2>&1 || true
        if git cherry-pick -x -X theirs "$SHA" >>"$LOG" 2>&1; then
            NEW=$(git rev-parse --short=12 HEAD)
            printf '%s\t%s\t%s\t%s\n' \
                "$SHORT" "$NEW" "$SUBJ" "${BUCKET}+theirs" >> "$RETRY_TSV"
            continue
        fi
    fi

    # ---- Tier 4: abort + REVIEW ---------------------------------------
    PATHS=$(echo "$CONFLICTED" | tr '\n' ',' | sed 's/,$//')
    if ! git cherry-pick --abort >>"$LOG" 2>&1; then
        die "cherry-pick --abort failed for $SHORT (paths=$PATHS)"
    fi
    printf '%s\t%s\tconflict:%s\n' "$SHORT" "$SUBJ" "$PATHS" >> "$FAILED_TSV"
done < "$CLASSIFY_TSV"

# ---- Summary ----------------------------------------------------------------

A=$(wc -l <"$APPLIED_TSV" | tr -d ' ')
R=$(wc -l <"$RETRY_TSV"   | tr -d ' ')
F=$(wc -l <"$FAILED_TSV"  | tr -d ' ')
N=$(wc -l <"$NEWS_PORT_TSV" | tr -d ' ')
log "applied=${A} retried=${R} failed=${F} news-port=${N}"

# ---- Report -----------------------------------------------------------------

REPORT_DIR=${REPO_ROOT}/.claude/notes
mkdir -p "$REPORT_DIR"
REPORT="${REPORT_DIR}/upstream-backport-review-${RUN_TS}.md"

ANCHOR_SUBJ=$(git show -s --format=%s "$ANCHOR")
ANCHOR_DATE_FMT=${ANCHOR_DATE%% *}

python3 "${SCRIPT_DIR}/report.py" \
    --run-dir "$RUN_DIR" \
    --classify-tsv "$CLASSIFY_TSV" \
    --applied-tsv "$APPLIED_TSV" \
    --retry-tsv "$RETRY_TSV" \
    --failed-tsv "$FAILED_TSV" \
    --news-port-tsv "$NEWS_PORT_TSV" \
    --anchor "$ANCHOR" \
    --anchor-subject "$ANCHOR_SUBJ" \
    --anchor-date "$ANCHOR_DATE_FMT" \
    --behind "$BEHIND" \
    --branch "$BRANCH" \
    --run-ts "$RUN_TS" \
    --output "$REPORT"

# Update latest pointer (rewrite as a tiny redirect file rather than
# symlink, for portability).
cat > "${REPORT_DIR}/upstream-backport-review-latest.md" <<EOF
Latest upstream-commit-review report:
[$(basename "$REPORT")]($(basename "$REPORT"))
EOF

log "report: $REPORT"

# ---- Optional smoke test ----------------------------------------------------

if [ "$SMOKE" -eq 1 ]; then
    log "running smoke tests"
    if meson test -C "${REPO_ROOT}/build" --suite smoke 2>&1 | tee -a "$LOG"; then
        log "smoke OK"
    else
        log "smoke FAILED — see $LOG"
        exit 2
    fi
fi
