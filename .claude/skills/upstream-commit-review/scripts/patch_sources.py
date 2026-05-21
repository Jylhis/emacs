#!/usr/bin/env python3
"""Patch-source poll step for upstream-commit-review.

Clones every source listed in ``attributes/patch-sources.toml``
shallowly into a scratch directory, hashes the patch files matching
each source's globs, and diffs against the baseline in
``scripts/state/patch-sources.json``.  Emits a TSV the report renderer
consumes, plus the per-patch verdicts stored alongside the baseline
hashes.

Invocation modes:

    patch_sources.py --report-tsv PATH
        Compare clones against the baseline and write a TSV
        (name <TAB> patch_path <TAB> status <TAB> verdict <TAB> note)
        where status is one of {new, changed, removed, unchanged}.
        Does not modify the baseline.

    patch_sources.py --update-baseline
        Refresh the baseline JSON in place to match what the sources
        currently ship.  Preserves existing per-patch verdict/note
        fields when the path is unchanged.

Both modes are idempotent.  Clones live under ${RUN_DIR}/sources/ and
are not persisted in the repo.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

DEFAULT_VERDICT = "unreviewed"
_VALID_VERDICTS = frozenset(
    {"absorb-now", "verify-then-absorb", "defer",
     "not-applicable", "unreviewed"}
)


def load_manifest(path: Path) -> list[dict]:
    """Parse the TOML manifest and return its [[source]] entries."""
    raw = tomllib.loads(path.read_text())
    sources = raw.get("source", [])
    if not isinstance(sources, list):
        raise ValueError(f"{path}: 'source' must be an array of tables")
    for src in sources:
        for key in ("name", "url", "branch", "globs"):
            if key not in src:
                raise ValueError(
                    f"{path}: source missing required key '{key}': {src!r}"
                )
        if not isinstance(src["globs"], list) or not src["globs"]:
            raise ValueError(
                f"{path}: source {src['name']!r} 'globs' must be a non-empty list"
            )
    return sources


def load_baseline(path: Path) -> dict:
    """Load the baseline JSON; tolerate the seed file shape."""
    if not path.exists():
        return {"sources": {}}
    raw = json.loads(path.read_text())
    raw.setdefault("sources", {})
    return raw


def save_baseline(path: Path, data: dict) -> None:
    """Write the baseline JSON with stable key order."""
    # Sort source names; sort paths within each source for deterministic
    # diffs in version control.
    ordered = {"_doc": data.get(
        "_doc",
        "Baseline SHA-256 hashes for tracked patch files; updated by "
        "patch_sources.py --update-baseline. Schema: { sources: { <name>: "
        "{ <path>: { sha256, verdict, note } } } }. Verdicts: absorb-now | "
        "verify-then-absorb | defer | not-applicable | unreviewed."
    ), "sources": {}}
    for name in sorted(data["sources"]):
        entries = data["sources"][name]
        ordered["sources"][name] = {
            p: entries[p] for p in sorted(entries)
        }
    path.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n")


def clone_source(src: dict, dest: Path) -> None:
    """Shallow-clone a source into ``dest``.

    Uses ``--depth=1 --filter=blob:none`` so each clone is light; a
    follow-up ``checkout`` materialises only the blobs we touch via
    ``git ls-files``/``git cat-file``.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        # Refresh: fetch + reset hard.
        subprocess.run(
            ["git", "-C", str(dest), "fetch", "--depth=1",
             "origin", src["branch"]],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(dest), "reset", "--hard", "FETCH_HEAD"],
            check=True, capture_output=True,
        )
        return
    subprocess.run(
        ["git", "clone", "--quiet", "--depth=1",
         "--filter=blob:none",
         "--branch", src["branch"], src["url"], str(dest)],
        check=True, capture_output=True,
    )


def list_patches(repo: Path, globs: list[str]) -> dict[str, str]:
    """Return ``{relpath: sha256}`` for every file in ``repo`` matching
    any glob.  Glob matching uses fnmatch on the POSIX path."""
    # Use `git ls-files` so we honour the repo's index (avoids picking
    # up stray files left by previous runs in the worktree).
    out = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files"], text=True
    )
    selected = []
    for path in out.splitlines():
        for glob in globs:
            if fnmatch.fnmatch(path, glob):
                selected.append(path)
                break
    result: dict[str, str] = {}
    for rel in selected:
        body = (repo / rel).read_bytes()
        result[rel] = hashlib.sha256(body).hexdigest()
    return result


def diff_against_baseline(
    current: dict[str, str],
    baseline: dict[str, dict],
) -> list[tuple[str, str, str, str]]:
    """Compute (path, status, verdict, note) rows.

    ``status`` is one of ``new``, ``changed``, ``removed``, ``unchanged``.
    Baseline entries are ``{sha256, verdict?, note?}`` dicts.
    """
    rows: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for path in sorted(current):
        seen.add(path)
        new_hash = current[path]
        entry = baseline.get(path)
        if entry is None:
            rows.append((path, "new", DEFAULT_VERDICT, ""))
        elif entry.get("sha256") != new_hash:
            rows.append((
                path, "changed",
                entry.get("verdict", DEFAULT_VERDICT),
                entry.get("note", ""),
            ))
        else:
            rows.append((
                path, "unchanged",
                entry.get("verdict", DEFAULT_VERDICT),
                entry.get("note", ""),
            ))
    for path in sorted(baseline):
        if path in seen:
            continue
        entry = baseline[path]
        rows.append((
            path, "removed",
            entry.get("verdict", DEFAULT_VERDICT),
            entry.get("note", ""),
        ))
    return rows


def cmd_report(args) -> int:
    manifest_path = Path(args.manifest)
    baseline_path = Path(args.baseline)
    sources = load_manifest(manifest_path)
    baseline = load_baseline(baseline_path)
    out_lines: list[str] = []
    for src in sources:
        name = src["name"]
        dest = Path(args.run_dir) / "sources" / name
        try:
            clone_source(src, dest)
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or b"").decode(errors="replace").strip()
            sys.stderr.write(
                f"[patch-sources] clone failed for {name}: {stderr}\n"
            )
            out_lines.append(
                f"{name}\t(clone-failed)\terror\tunknown\t{stderr[:120]}"
            )
            continue
        current = list_patches(dest, src["globs"])
        rows = diff_against_baseline(
            current, baseline["sources"].get(name, {})
        )
        for path, status, verdict, note in rows:
            out_lines.append(
                f"{name}\t{path}\t{status}\t{verdict}\t{note}"
            )
    Path(args.report_tsv).write_text("\n".join(out_lines) + "\n")
    return 0


def cmd_update_baseline(args) -> int:
    manifest_path = Path(args.manifest)
    baseline_path = Path(args.baseline)
    sources = load_manifest(manifest_path)
    baseline = load_baseline(baseline_path)
    for src in sources:
        name = src["name"]
        dest = Path(args.run_dir) / "sources" / name
        clone_source(src, dest)
        current = list_patches(dest, src["globs"])
        prev = baseline["sources"].get(name, {})
        next_entries: dict[str, dict] = {}
        for path, sha in current.items():
            old = prev.get(path, {})
            next_entries[path] = {
                "sha256": sha,
                "verdict": old.get("verdict", DEFAULT_VERDICT),
                "note": old.get("note", ""),
            }
        baseline["sources"][name] = next_entries
    save_baseline(baseline_path, baseline)
    sys.stderr.write(
        f"[patch-sources] baseline updated: {baseline_path}\n"
    )
    return 0


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    default_manifest = here.parent / "attributes" / "patch-sources.toml"
    default_baseline = here / "state" / "patch-sources.json"
    default_rundir = Path(
        os.environ.get("RUN_DIR")
        or os.environ.get("TMPDIR", "/tmp")
    ) / "upstream-commit-review-patch-sources"

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", default=str(default_manifest))
    p.add_argument("--baseline", default=str(default_baseline))
    p.add_argument("--run-dir", default=str(default_rundir))
    sub = p.add_subparsers(dest="mode", required=False)

    rep = sub.add_parser("report", help="emit comparison TSV")
    rep.add_argument("--report-tsv", required=True)
    rep.set_defaults(func=cmd_report)

    upd = sub.add_parser("update-baseline",
                         help="refresh state/patch-sources.json")
    upd.set_defaults(func=cmd_update_baseline)

    args = p.parse_args(argv)
    if args.mode is None:
        p.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
