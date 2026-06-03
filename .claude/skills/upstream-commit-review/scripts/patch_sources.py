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
from pathlib import PurePosixPath
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

DEFAULT_VERDICT = "unreviewed"
MAX_PATCH_BYTES = 16 * 1024 * 1024
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


class UnsafePatchError(ValueError):
    """Raised when a matched patch path is unsafe to hash."""


def _selected_index_entries(
    repo: Path, globs: list[str]
) -> list[tuple[str, str, str]]:
    """Return ``(mode, object_id, path)`` entries matching the globs."""
    # Use `git ls-files` so we honour the repo's index (avoids picking
    # up stray files left by previous runs in the worktree).  Include the
    # staged mode/object id and consume NUL-separated records so later hashing
    # can read Git blob objects directly instead of following worktree paths.
    out = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "-s", "-z"],
        text=True,
    )
    selected = []
    for entry in out.split("\0"):
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        mode, object_id, _stage = metadata.split(" ", 2)
        pp = PurePosixPath(path)
        for glob in globs:
            if pp.match(glob):
                selected.append((mode, object_id, path))
                break
    return selected


def _hash_git_blob(repo: Path, object_id: str, rel: str) -> str:
    """Hash a Git blob by object id without reading through the worktree."""
    size_text = subprocess.check_output(
        ["git", "-C", str(repo), "cat-file", "-s", object_id],
        text=True,
    ).strip()
    size = int(size_text)
    if size > MAX_PATCH_BYTES:
        raise UnsafePatchError(
            f"{rel}: patch blob is {size} bytes; limit is {MAX_PATCH_BYTES}"
        )

    cmd = ["git", "-C", str(repo), "cat-file", "blob", object_id]
    hasher = hashlib.sha256()
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        assert proc.stdout is not None
        for chunk in iter(lambda: proc.stdout.read(1024 * 1024), b""):
            hasher.update(chunk)
        if proc.wait() != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd)
    return hasher.hexdigest()


def list_patches(repo: Path, globs: list[str]) -> dict[str, str]:
    """Return ``{relpath: sha256}`` for every file in ``repo`` matching
    any glob.  Glob matching uses ``PurePosixPath.match`` so ``*`` does
    NOT cross directory boundaries — that prevents a glob like
    ``pkgs/applications/editors/emacs/*.patch`` from silently picking
    up patches several levels deeper (e.g. under
    ``elisp-packages/manual-packages/``).  To recurse, write the glob
    explicitly with ``**`` or list each subdir."""
    result: dict[str, str] = {}
    for mode, object_id, rel in _selected_index_entries(repo, globs):
        if mode not in {"100644", "100755"}:
            raise UnsafePatchError(
                f"{rel}: refusing to hash non-regular git mode {mode}"
            )
        result[rel] = _hash_git_blob(repo, object_id, rel)
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
        try:
            current = list_patches(dest, src["globs"])
        except UnsafePatchError as exc:
            sys.stderr.write(
                f"[patch-sources] unsafe patch source for {name}: {exc}\n"
            )
            out_lines.append(
                f"{name}\t(unsafe-patch-source)\terror\tunknown\t{str(exc)[:120]}"
            )
            continue
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
