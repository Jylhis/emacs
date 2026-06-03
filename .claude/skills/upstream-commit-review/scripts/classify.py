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
import glob
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

DOC_ONLY_RX = re.compile(
    r"^doc/"
    r"|^etc/(NEWS(\.[0-9]+)?|ERC-NEWS|HISTORY|AUTHORS)$"
    r"|\.texi(nfo)?$"
    r"|\.org$"
)
TEST_ONLY_RX = re.compile(r"^test/")
LISP_RX = re.compile(r"^lisp/.+\.el$")
LISP_OR_TEST_RX = re.compile(r"^(lisp/|test/)")
SRC_RX = re.compile(r"^src/")
LISP_TEST_NEWS_RX = re.compile(r"^(lisp/|test/)|^etc/NEWS(\.[0-9]+)?$")

DOC_STYLE_SUBJ_RX = re.compile(
    r"\b(docstring|doc string|doc fix|typo|when-let|comment fix)\b",
    re.IGNORECASE,
)
SMALL_SRC_PREFIX_RX = re.compile(
    r"^(Fix |; Fix |Pacify |Avoid |; Avoid |Don't |; \* src/)"
)
FEATURE_SUBJ_RX = re.compile(r"^(Add|New|Introduce)\b")
BUG_RX = re.compile(r"\bBug#\d+", re.IGNORECASE)


# ---- Data model -------------------------------------------------------------

@dataclass
class Commit:
    sha: str
    subject: str
    files: list[str] = field(default_factory=list)
    lines: int = 0

    @property
    def missing_file(self) -> str | None:
        for f in self.files:
            # This fork keeps NEWS as versioned files (e.g. etc/NEWS.31).
            # Treat upstream etc/NEWS as present when any versioned NEWS
            # file exists so NEWS-related AUTO rules remain reachable.
            if f == "etc/NEWS":
                if os.path.exists("etc/NEWS"):
                    continue
                if glob.glob("etc/NEWS.[0-9]*"):
                    continue
            if not os.path.exists(f):
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
        return self.bucket in {"autotools", "merge-noise", "admin"}


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

    # Missing-file forces REVIEW regardless of file pattern.
    missing = c.missing_file
    if missing is not None:
        return Decision("review", f"missing-file:{missing}")

    # Rule 4: AUTO / doc-only
    if all_match(files, DOC_ONLY_RX):
        return Decision("doc-only", "doc-only")

    # Rule 5: AUTO / test-only
    if all_match(files, TEST_ONLY_RX):
        return Decision("test-only", "test-only")

    # Rule 6: AUTO / lisp bugfix
    if BUG_RX.search(subj) and all_match(files, LISP_OR_TEST_RX):
        return Decision("lisp-bugfix", "lisp+test, has Bug#")

    # Rule 7: AUTO / lisp doc-or-style fix
    if (all_match(files, LISP_RX)
            and c.lines < 50
            and (subj.startswith("; ") or DOC_STYLE_SUBJ_RX.search(subj))):
        return Decision("lisp-doc-style", "lisp doc/style, < 50 lines")

    # Rule 8: AUTO / small src fix
    if all_match(files, SRC_RX) and c.lines < 50:
        if (SMALL_SRC_PREFIX_RX.search(subj)
                or BUG_RX.search(subj)
                or c.lines < 20):
            return Decision("small-src", "src/ < 50 lines, fix-shape")

    # Rule 9: AUTO / lisp+NEWS Bug#
    if BUG_RX.search(subj) and all_match(files, LISP_TEST_NEWS_RX):
        return Decision("lisp+news-bug", "lisp+test+NEWS, has Bug#")

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
    if in_lisp and not BUG_RX.search(c.subject):
        return "lisp-no-bug"
    return "unclassified"


# ---- Git plumbing -----------------------------------------------------------

# The chosen format uses single-character record separators rather than
# tabs because file lists can contain spaces.  Field separator: \x1f
# Record separator: \x1e
GIT_FORMAT = "%H%x1f%s"


def gather(shas: list[str]) -> list[Commit]:
    """Gather commit metadata in one pass per ~100 SHAs.

    Returns commits in the order given by `shas`.
    """
    out: list[Commit] = []
    if not shas:
        return out
    for chunk in _chunks(shas, 100):
        # Subjects in one batched call.
        meta = subprocess.check_output(
            ["git", "log", "--no-walk=unsorted", f"--format={GIT_FORMAT}",
             *chunk],
            text=True,
        )
        meta_map: dict[str, str] = {}
        for line in meta.split("\n"):
            if not line:
                continue
            sha, _, subject = line.partition("\x1f")
            meta_map[sha] = subject
        # Files + shortstat per commit.  `git show` is per-commit; we
        # batch via xargs-style loop but each is sub-millisecond.
        for sha in chunk:
            files = _files_for(sha)
            lines = _lines_for(sha)
            out.append(Commit(
                sha=sha,
                subject=meta_map.get(sha, ""),
                files=files,
                lines=lines,
            ))
    return out


def _chunks(seq: list[str], n: int) -> Iterable[list[str]]:
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _files_for(sha: str) -> list[str]:
    raw = subprocess.check_output(
        ["git", "show", "--name-only", "--format=", sha],
        text=True,
    )
    return [f for f in raw.splitlines() if f]


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
