#!/usr/bin/env python3
"""Render the markdown report from apply.sh's TSV state files.

Invoked by apply.sh; not meant for direct use.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def read_tsv(path: str) -> list[list[str]]:
    if not os.path.exists(path):
        return []
    rows: list[list[str]] = []
    with open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            rows.append(line.split("\t"))
    return rows


def group_review_by_area(rows: list[list[str]]) -> dict[str, list[list[str]]]:
    """Bucket REVIEW rows by primary directory of their first file."""
    groups: dict[str, list[list[str]]] = defaultdict(list)
    for row in rows:
        if len(row) < 5:
            continue
        sha, bucket, reason, lines, files = row[:5]
        if bucket != "review":
            continue
        first = files.split(",")[0] if files else ""
        area = _area_for(first)
        groups[area].append([sha, "", reason, lines, files])
    return groups


def _area_for(path: str) -> str:
    if path.startswith("src/"):
        return "src/"
    if path.startswith("lisp/"):
        # Two-level grouping under lisp/.
        parts = path.split("/")
        if len(parts) >= 3:
            return "/".join(parts[:2]) + "/"
        return "lisp/"
    if path.startswith(("doc/", "etc/", "lib-src/", "test/", "admin/",
                        "nextstep/")):
        return path.split("/")[0] + "/"
    return "other"


def range_diff(orig_sha: str, new_sha: str, max_lines: int = 30) -> str:
    """Run git range-diff for the single-commit pair and truncate."""
    try:
        out = subprocess.check_output(
            ["git", "range-diff", "--no-color",
             f"{orig_sha}~..{orig_sha}", f"{new_sha}~..{new_sha}"],
            text=True, stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        out = exc.output or "(range-diff failed)"
    lines = out.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [
            f"... ({len(out.splitlines()) - max_lines} more lines truncated)"]
    return "\n".join(lines)


def difft_excerpt(new_sha: str, max_lines: int = 30) -> str:
    """Render the commit's diff via difftastic if available."""
    if not shutil.which("difft"):
        return ""
    try:
        out = subprocess.check_output(
            ["git", "show", "--ext-diff", "--color=never",
             "--format=", new_sha],
            env={**os.environ,
                 "GIT_EXTERNAL_DIFF":
                     "difft --color=never --display=inline --width=120"},
            text=True,
        )
    except subprocess.CalledProcessError:
        return ""
    lines = out.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [
            f"... ({len(out.splitlines()) - max_lines} more lines truncated)"]
    return "\n".join(lines)


def render(args) -> str:
    classify_rows = read_tsv(args.classify_tsv)
    applied_rows = read_tsv(args.applied_tsv)
    retry_rows = read_tsv(args.retry_tsv)
    failed_rows = read_tsv(args.failed_tsv)
    news_rows = read_tsv(args.news_port_tsv)
    patch_source_rows = (
        read_tsv(args.patch_sources_tsv)
        if getattr(args, "patch_sources_tsv", None) else []
    )

    n_total = len(classify_rows)
    n_applied = len(applied_rows)
    n_retry = len(retry_rows)
    n_failed = len(failed_rows)
    n_skip = sum(1 for r in classify_rows
                 if r[1] in {"autotools", "merge-noise", "admin",
                              "release-branch", "removed-area"})
    n_review = sum(1 for r in classify_rows if r[1] == "review")
    n_news = len(news_rows)

    lines: list[str] = []
    lines.append(f"# Upstream backport review — {args.run_ts} UTC")
    lines.append("")
    lines.append(f"- Anchor: `{args.anchor[:12]}` "
                 f"({args.anchor_subject}) — {args.anchor_date}")
    lines.append(f"- Range: `{args.anchor[:12]}..{args.branch}` "
                 f"vs emacs-upstream/master ({args.behind} behind)")
    lines.append(f"- Reviewed: {n_total}   "
                 f"Applied: {n_applied}   "
                 f"Retried (-X theirs): {n_retry}   "
                 f"Skipped: {n_skip}   "
                 f"Needs review: {n_review}   "
                 f"Failed (conflict): {n_failed}   "
                 f"News-port-required: {n_news}")
    lines.append("")

    # APPLIED
    lines.append("## Applied")
    lines.append("")
    if applied_rows:
        lines.append("| Original SHA | New SHA | Subject | Bucket |")
        lines.append("|---|---|---|---|")
        for r in applied_rows:
            sha, new, subj, bucket = (r + ["", "", "", ""])[:4]
            lines.append(f"| `{sha}` | `{new}` | {subj} | {bucket} |")
    else:
        lines.append("(none)")
    lines.append("")

    # RETRIED
    if retry_rows:
        lines.append("## Retried with -X theirs")
        lines.append("")
        lines.append("| Original SHA | New SHA | Subject | Bucket |")
        lines.append("|---|---|---|---|")
        for r in retry_rows:
            sha, new, subj, bucket = (r + ["", "", "", ""])[:4]
            lines.append(f"| `{sha}` | `{new}` | {subj} | {bucket} |")
        lines.append("")

    # NEEDS REVIEW (grouped)
    review_groups = group_review_by_area(classify_rows)
    if review_groups:
        lines.append("## Needs review (grouped by area)")
        lines.append("")
        order = ["src/", "lisp/", "doc/", "etc/", "lib-src/", "test/",
                 "admin/", "nextstep/", "other"]

        def area_key(area: str) -> tuple[int, str]:
            for i, prefix in enumerate(order):
                if area == prefix or area.startswith(prefix):
                    return (i, area)
            return (len(order), area)

        for area in sorted(review_groups.keys(), key=area_key):
            lines.append(f"### {area}")
            lines.append("")
            lines.append("| SHA | Subject | Lines | Why |")
            lines.append("|---|---|---|---|")
            for row in review_groups[area]:
                sha, _, reason, line_count, files = row[:5]
                # Look up subject from classify_rows
                subj = _subject_for(sha)
                lines.append(f"| `{sha[:12]}` | {subj} | "
                             f"{line_count} | {reason} |")
            lines.append("")

    # FAILED
    if failed_rows:
        lines.append("## Failed (cherry-pick aborted)")
        lines.append("")
        lines.append("| SHA | Subject | Conflict |")
        lines.append("|---|---|---|")
        for r in failed_rows:
            sha, subj, why = (r + ["", "", ""])[:3]
            lines.append(f"| `{sha}` | {subj} | {why} |")
        lines.append("")

    # SKIPPED
    skipped = [r for r in classify_rows
               if r[1] in {"autotools", "merge-noise", "admin",
                              "release-branch", "removed-area"}]
    if skipped:
        lines.append("## Skipped")
        lines.append("")
        lines.append("| SHA | Subject | Reason |")
        lines.append("|---|---|---|")
        for r in skipped:
            sha, bucket, reason, _, _ = r[:5]
            subj = _subject_for(sha)
            lines.append(f"| `{sha[:12]}` | {subj} | {bucket} |")
        lines.append("")

    # RANGE-DIFF section for retried commits
    if retry_rows:
        lines.append("## Range-diffs of -X theirs resolutions")
        lines.append("")
        lines.append("Each block compares the upstream commit "
                     "(`<orig>~..<orig>`) against its cherry-picked form "
                     "(`<new>~..<new>`).  Identical commits show no diff "
                     "lines; differences mark hunks taken from upstream "
                     "or kept from our local branch.")
        lines.append("")
        for r in retry_rows:
            sha, new, subj = r[:3]
            lines.append(f"### `{sha}` — {subj}")
            lines.append("")
            lines.append("```")
            lines.append(range_diff(sha, new))
            lines.append("```")
            lines.append("")

    # PATCH-SOURCE drift + candidates
    drift_rows = [r for r in patch_source_rows
                  if len(r) >= 3 and r[2] in {"new", "changed",
                                              "removed", "error"}]
    if drift_rows:
        lines.append("## Patch-source drift")
        lines.append("")
        lines.append("File-based patches tracked from external repos "
                     "(see `references/patch-sources.md`).  Status "
                     "compares the SHA-256 of each patch body against "
                     "`scripts/state/patch-sources.json`.")
        lines.append("")
        by_source: dict[str, list[list[str]]] = defaultdict(list)
        for row in drift_rows:
            by_source[row[0]].append(row)
        for src in sorted(by_source):
            lines.append(f"### {src}")
            lines.append("")
            lines.append("| Path | Status | Verdict | Note |")
            lines.append("|---|---|---|---|")
            for row in by_source[src]:
                # row layout: name, path, status, verdict, note?
                path = row[1]
                status = row[2]
                verdict = row[3] if len(row) >= 4 else ""
                note = row[4] if len(row) >= 5 else ""
                lines.append(
                    f"| `{path}` | {status} | {verdict} | {note} |"
                )
            lines.append("")
        # Highlight new rows for human action.
        new_rows = [r for r in drift_rows if r[2] == "new"]
        if new_rows:
            lines.append("#### New patches awaiting verdict")
            lines.append("")
            lines.append("Run `python3 scripts/patch_sources.py "
                         "update-baseline` after writing per-patch "
                         "verdicts into `scripts/state/patch-sources.json`. "
                         "Verdict values: `absorb-now`, "
                         "`verify-then-absorb`, `defer`, `not-applicable`.")
            lines.append("")
            for r in new_rows:
                lines.append(f"- **{r[0]}** — `{r[1]}`")
            lines.append("")

    # NEWS-port section
    if news_rows:
        lines.append("## NEWS hunks needing port to etc/NEWS.31")
        lines.append("")
        lines.append("These commits had their `etc/NEWS` hunk auto-merged "
                     "into `etc/NEWS.31` via Git's rename-detection.  Inspect "
                     "the range-diff above for each entry to verify the "
                     "section ordering matches `etc/NEWS.31`'s structure.")
        lines.append("")
        for r in news_rows:
            sha, subj = r[:2]
            lines.append(f"- `{sha}` — {subj}")
        lines.append("")

    return "\n".join(lines) + "\n"


def _subject_for(sha: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "show", "-s", "--format=%s", sha], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "(subject unavailable)"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", required=True)
    p.add_argument("--classify-tsv", required=True)
    p.add_argument("--applied-tsv", required=True)
    p.add_argument("--retry-tsv", required=True)
    p.add_argument("--failed-tsv", required=True)
    p.add_argument("--news-port-tsv", required=True)
    p.add_argument("--patch-sources-tsv", required=False, default="")
    p.add_argument("--anchor", required=True)
    p.add_argument("--anchor-subject", required=True)
    p.add_argument("--anchor-date", required=True)
    p.add_argument("--behind", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--run-ts", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)

    Path(args.output).write_text(render(args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
