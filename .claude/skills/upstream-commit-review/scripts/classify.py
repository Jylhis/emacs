#!/usr/bin/env python3
"""Classify upstream candidate commits into AUTO / SKIP / REVIEW
buckets per the rules in SKILL.md.

Reads the candidate SHA list from stdin (one full SHA per line),
or computes it from the configured range if --compute-range is
passed.  Emits a TSV to stdout with columns:

    sha  bucket  reason  lines  files

Buckets:
    autotools, merge-noise, admin                        (SKIP)
    doc-only, test-only, lisp-bugfix, lisp-doc-style,
    small-src, lisp+news-bug                              (AUTO)
    review                                                (REVIEW; reason
                                                          carries the why)

The script does at most one git invocation per ~50 commits via a
batched `git log --format=...` pull, so it stays sub-second on
~150 candidates.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Iterable

# ---- Rule constants (mirrored in SKILL.md) ----------------------------------

AUTOTOOLS_RX = re.compile(
    r"^(configure\.ac|autogen\.sh|make-dist|GNUmakefile)$"
    r"|Makefile\.in$"
    r"|^m4/"
)
ADMIN_RX = re.compile(r"^admin/|^ChangeLog(\.[0-9]+)?$|^etc/MAINTAINERS$")
MERGE_SUBJECT_RX = re.compile(r"^(; *)?Merge \b|gitmerge", re.IGNORECASE)
# Release-branch-only commits.  These appear on emacs-NN release branches
# and travel to master only as merge commits; the standalone commit on
# the release branch does not apply cleanly to master-tracking forks.
RELEASE_BRANCH_SUBJ_RX = re.compile(
    r"^(Change \w+ version for Emacs \d+ to "
    r"|Cut the emacs-\d+ release branch"
    r"|Bump (master )?Emacs version)",
    re.IGNORECASE,
)

DOC_ONLY_RX = re.compile(
    r"^doc/"
    r"|^etc/(NEWS(\.[0-9]+)?|ERC-NEWS|HISTORY|AUTHORS|PROBLEMS)$"
    r"|\.texi(nfo)?$"
    r"|\.org$"
)
TEST_ONLY_RX = re.compile(r"^test/")
LISP_RX = re.compile(r"^lisp/.+\.el$")
LISP_OR_TEST_RX = re.compile(r"^(lisp/|test/)")
SRC_RX = re.compile(r"^src/")
LISP_TEST_NEWS_RX = re.compile(r"^(lisp/|test/|doc/)|^etc/NEWS(\.[0-9]+)?$")

DOC_STYLE_SUBJ_RX = re.compile(
    r"\b(docstring|doc string|doc fix|typo|when-let|comment fix)\b",
    re.IGNORECASE,
)
# Small-src cleanup-shape prefixes.  Used as a permissive gate alongside
# size + Bug#; not the only signal.
SMALL_SRC_SHAPE_RX = re.compile(
    r"^(Fix |; Fix |Pacify |Avoid |; Avoid |Don't |; \* src/)"
)
FEATURE_SUBJ_RX = re.compile(r"^(Add|New|Introduce)\b")
BUG_RX = re.compile(r"\bBug#\d+", re.IGNORECASE)


# ---- Data model -------------------------------------------------------------

# Renames applied at the cutover: upstream paths that map to a different
# path in this fork.  Used by missing_file() so commits that touch
# upstream's `etc/NEWS` don't trip the missing-file demotion — git's
# rename detection already routes them to `etc/NEWS.31` at cherry-pick.
RENAMED_TO: dict[str, str] = {
    "etc/NEWS": "etc/NEWS.31",
}


@dataclass
class Commit:
    sha: str
    subject: str
    body: str = ""
    files: list[str] = field(default_factory=list)
    # Files the commit ADDS (status `A` in `git show --name-status`).
    # These are excluded from the missing_file check because the commit
    # creates them — the absence in HEAD is expected.
    added_files: set[str] = field(default_factory=set)
    lines: int = 0

    @property
    def has_bug(self) -> bool:
        """Bug#NNNN in subject OR body."""
        return bool(BUG_RX.search(self.subject)
                    or (self.body and BUG_RX.search(self.body)))

    @property
    def missing_file(self) -> str | None:
        for f in self.files:
            # A commit that adds a file naturally doesn't have it in HEAD.
            if f in self.added_files:
                continue
            # Rename: treat upstream path as if it were the renamed path.
            check = RENAMED_TO.get(f, f)
            if not os.path.exists(check):
                return f
        return None


@dataclass
class Decision:
    bucket: str  # one of the constants below
    reason: str  # short tag for the report's Why column

    def is_auto(self) -> bool:
        return self.bucket in {
            "doc-only", "test-only", "lisp-bugfix",
            "lisp-doc-style", "small-src", "lisp+news-bug",
        }

    def is_skip(self) -> bool:
        return self.bucket in {"autotools", "merge-noise", "admin",
                               "release-branch"}


# ---- Rule engine ------------------------------------------------------------

def all_match(files: Iterable[str], rx: re.Pattern[str]) -> bool:
    files = list(files)
    return bool(files) and all(rx.search(f) for f in files)


def any_match(files: Iterable[str], rx: re.Pattern[str]) -> bool:
    return any(rx.search(f) for f in files)


def classify(c: Commit) -> Decision:
    """Apply the rule ladder.  First match wins."""
    files = c.files
    subj = c.subject

    # Rule 1: SKIP / autotools
    if any_match(files, AUTOTOOLS_RX):
        return Decision("autotools", "build-system: autotools")

    # Rule 2: SKIP / merge-noise
    if MERGE_SUBJECT_RX.search(subj):
        return Decision("merge-noise", "merge commit / gitmerge")

    # Rule 3: SKIP / admin churn
    if all_match(files, ADMIN_RX):
        return Decision("admin", "admin/ or ChangeLog only")

    # Rule 3.5: SKIP / release-branch-only commit.  These travel to
    # master via merges; the standalone commit doesn't apply.
    if RELEASE_BRANCH_SUBJ_RX.search(subj):
        return Decision("release-branch", "release-branch commit")

    # Missing-file forces REVIEW regardless of file pattern.
    # (added_files and renamed paths handled inside missing_file.)
    missing = c.missing_file
    if missing is not None:
        return Decision("review", f"missing-file:{missing}")

    # Rule 4: AUTO / doc-only
    if all_match(files, DOC_ONLY_RX):
        return Decision("doc-only", "doc-only")

    # Rule 5: AUTO / test-only
    if all_match(files, TEST_ONLY_RX):
        return Decision("test-only", "test-only")

    # Rule 6: AUTO / lisp bugfix (Bug# anywhere in subject or body)
    if c.has_bug and all_match(files, LISP_OR_TEST_RX):
        return Decision("lisp-bugfix", "lisp+test, has Bug#")

    # Rule 7: AUTO / lisp doc-or-style fix
    if (all_match(files, LISP_RX)
            and c.lines < 50
            and (subj.startswith("; ") or DOC_STYLE_SUBJ_RX.search(subj))):
        return Decision("lisp-doc-style", "lisp doc/style, < 50 lines")

    # Rule 8: AUTO / small src fix.  Any src/-only change under 50
    # lines is auto-applied if any of:
    #   - it is tiny (< 20 lines),
    #   - it carries a Bug# tag anywhere (subject or body),
    #   - its subject matches a cleanup shape (Fix/Pacify/Avoid/...).
    if all_match(files, SRC_RX) and c.lines < 50:
        if (c.has_bug
                or c.lines < 20
                or SMALL_SRC_SHAPE_RX.search(subj)):
            return Decision("small-src", "src/ < 50 lines")

    # Rule 9: AUTO / lisp+doc+NEWS Bug#.  Extended from the original
    # lisp+test+NEWS rule to cover the very common "feature/fix + doc +
    # NEWS" pattern of mature subsystems (Eglot, Tramp, ERC, Gnus).
    if c.has_bug and all_match(files, LISP_TEST_NEWS_RX):
        return Decision("lisp+news-bug", "lisp+test+doc+NEWS, has Bug#")

    # Rule 11 (REVIEW with feature tag) — eyeballs required even if small.
    if FEATURE_SUBJ_RX.search(subj):
        return Decision("review", "feature")

    # Default REVIEW with a best-effort tag describing the near-miss.
    return Decision("review", _review_reason(c))


def _review_reason(c: Commit) -> str:
    files = c.files
    in_lisp = any(LISP_RX.search(f) for f in files)
    in_src = any(SRC_RX.search(f) for f in files)
    in_doc = any_match(files, DOC_ONLY_RX)
    in_admin = any(ADMIN_RX.search(f) for f in files)

    if c.lines >= 200:
        return "large"
    if in_lisp and in_src:
        return "lisp+src"
    if in_lisp and (in_doc or in_admin):
        return "lisp-multi-area"
    if in_src and len(files) > 1:
        return "src-multi-file"
    if in_lisp and not c.has_bug:
        return "lisp-no-bug"
    return "unclassified"


# ---- Git plumbing -----------------------------------------------------------

# The chosen format uses single-character record separators rather than
# tabs because file lists and commit bodies can contain spaces and
# newlines.  Field separator: \x1f  Body terminator: \x1e (record-end).
GIT_FORMAT = "%H%x1f%s%x1f%b%x1e"


def gather(shas: list[str]) -> list[Commit]:
    """Gather commit metadata in one pass per ~100 SHAs.

    Returns commits in the order given by `shas`.
    """
    out: list[Commit] = []
    if not shas:
        return out
    for chunk in _chunks(shas, 100):
        # Subjects and bodies in one batched call.
        meta = subprocess.check_output(
            ["git", "log", "--no-walk=unsorted", f"--format={GIT_FORMAT}",
             *chunk],
            text=True,
        )
        meta_map: dict[str, tuple[str, str]] = {}
        for record in meta.split("\x1e"):
            record = record.strip("\n")
            if not record:
                continue
            parts = record.split("\x1f", 2)
            if len(parts) < 2:
                continue
            sha = parts[0]
            subject = parts[1]
            body = parts[2] if len(parts) > 2 else ""
            meta_map[sha] = (subject, body)
        # Files + shortstat per commit.  `git show` is per-commit; we
        # batch via xargs-style loop but each is sub-millisecond.
        for sha in chunk:
            files, added = _files_for(sha)
            lines = _lines_for(sha)
            subject, body = meta_map.get(sha, ("", ""))
            out.append(Commit(
                sha=sha,
                subject=subject,
                body=body,
                files=files,
                added_files=added,
                lines=lines,
            ))
    return out


def _chunks(seq: list[str], n: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _files_for(sha: str) -> tuple[list[str], set[str]]:
    """Return (all_files, added_files) for SHA via --name-status."""
    raw = subprocess.check_output(
        ["git", "show", "--name-status", "--format=", sha],
        text=True,
    )
    files: list[str] = []
    added: set[str] = set()
    for line in raw.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        # Renames look like "R100\told\tnew" — record the new path.
        if status.startswith("R") and len(parts) >= 3:
            files.append(parts[2])
            continue
        if len(parts) < 2:
            continue
        path = parts[1]
        files.append(path)
        if status == "A":
            added.add(path)
    return files, added


_SHORTSTAT_NUM_RX = re.compile(r"(\d+) (insertion|deletion)")


def _lines_for(sha: str) -> int:
    raw = subprocess.check_output(
        ["git", "show", "--shortstat", "--format=", sha],
        text=True,
    )
    return sum(int(m.group(1)) for m in _SHORTSTAT_NUM_RX.finditer(raw))


def candidate_shas(remote_ref: str = "emacs-upstream/master",
                   trailer_set_path: str | None = None) -> list[str]:
    """Compute candidates: cherry-pick filter minus trailer-set."""
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip()
    raw = subprocess.check_output(
        ["git", "log", "--reverse", "--no-merges",
         "--cherry-pick", "--right-only",
         "--format=%H", f"{head}...{remote_ref}"],
        text=True,
    )
    shas = [s for s in raw.splitlines() if s]
    if trailer_set_path and os.path.exists(trailer_set_path):
        with open(trailer_set_path) as fh:
            already = {line.strip() for line in fh if line.strip()}
        shas = [s for s in shas if s not in already]
    return shas


# ---- CLI --------------------------------------------------------------------

def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--compute-range", action="store_true",
                   help="Compute candidates from emacs-upstream/master "
                        "instead of reading SHAs from stdin")
    p.add_argument("--remote-ref", default="emacs-upstream/master")
    p.add_argument("--trailer-set", default=None,
                   help="Path to a sorted file of already-cherry-picked SHAs")
    args = p.parse_args(argv)

    # Run from the repo root so missing-file checks (`os.path.exists`)
    # resolve relative paths against the working tree, not the script's
    # cwd.  All git invocations are repo-aware; this only affects the
    # filesystem stat calls in Commit.missing_file.
    repo_root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True).strip()
    os.chdir(repo_root)

    if args.compute_range:
        shas = candidate_shas(args.remote_ref, args.trailer_set)
    else:
        shas = [line.strip() for line in sys.stdin if line.strip()]

    commits = gather(shas)
    for c in commits:
        d = classify(c)
        files_join = ",".join(c.files[:5])
        if len(c.files) > 5:
            files_join += "…"
        print(f"{c.sha}\t{d.bucket}\t{d.reason}\t{c.lines}\t{files_join}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
