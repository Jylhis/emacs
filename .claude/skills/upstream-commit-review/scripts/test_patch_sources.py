#!/usr/bin/env python3
"""Unit tests for patch_sources.py.

Network-free: every test stages a fake repo on disk and drives the
module's pure helpers directly.  No clones, no real git remotes.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import patch_sources as ps


def _git(cwd: Path, *args: str) -> None:
    env = {
        "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    import os
    full = {**os.environ, **env}
    subprocess.run(["git", "-C", str(cwd), *args],
                   check=True, capture_output=True, env=full)


def _seed_repo(root: Path, files: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "main")
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        _git(root, "add", rel)
    _git(root, "commit", "-q", "-m", "seed")


class ManifestTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.toml"
            p.write_text(textwrap.dedent("""
                [[source]]
                name = "x"
                url = "https://example.com/x"
                branch = "main"
                globs = ["a/*.patch", "b/*.diff"]
            """))
            got = ps.load_manifest(p)
            self.assertEqual(len(got), 1)
            self.assertEqual(got[0]["name"], "x")
            self.assertEqual(got[0]["globs"], ["a/*.patch", "b/*.diff"])

    def test_missing_key(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.toml"
            p.write_text(textwrap.dedent("""
                [[source]]
                name = "x"
                url = "https://example.com/x"
                branch = "main"
            """))
            with self.assertRaisesRegex(ValueError, "globs"):
                ps.load_manifest(p)

    def test_empty_globs(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.toml"
            p.write_text(textwrap.dedent("""
                [[source]]
                name = "x"
                url = "https://example.com/x"
                branch = "main"
                globs = []
            """))
            with self.assertRaisesRegex(ValueError, "non-empty"):
                ps.load_manifest(p)


class ListPatchesTests(unittest.TestCase):
    def test_globs_filter(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _seed_repo(repo, {
                "patches/emacs-31/a.patch": "AAA\n",
                "patches/emacs-31/b.patch": "BBB\n",
                "patches/emacs-30/c.patch": "CCC\n",
                "README.md": "ignore",
            })
            got = ps.list_patches(repo, ["patches/emacs-31/*.patch"])
            self.assertEqual(set(got), {
                "patches/emacs-31/a.patch",
                "patches/emacs-31/b.patch",
            })
            self.assertEqual(
                got["patches/emacs-31/a.patch"],
                hashlib.sha256(b"AAA\n").hexdigest(),
            )

    def test_multi_glob_union(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            _seed_repo(repo, {
                "x/a.patch": "1",
                "x/b.diff": "2",
                "x/c.txt": "3",
            })
            got = ps.list_patches(repo, ["x/*.patch", "x/*.diff"])
            self.assertEqual(set(got), {"x/a.patch", "x/b.diff"})


class DiffTests(unittest.TestCase):
    def test_new_changed_removed_unchanged(self):
        current = {
            "a.patch": "h1",
            "b.patch": "h2-new",
            "c.patch": "h3",
        }
        baseline = {
            "a.patch": {"sha256": "h1", "verdict": "absorb-now",
                        "note": "land it"},
            "b.patch": {"sha256": "h2-old", "verdict": "defer", "note": ""},
            "removed.patch": {"sha256": "hX",
                              "verdict": "not-applicable",
                              "note": "gone"},
        }
        rows = ps.diff_against_baseline(current, baseline)
        by_path = {r[0]: r for r in rows}
        self.assertEqual(by_path["a.patch"][1], "unchanged")
        self.assertEqual(by_path["a.patch"][2], "absorb-now")
        self.assertEqual(by_path["b.patch"][1], "changed")
        # changed rows keep the old verdict so the human can re-review.
        self.assertEqual(by_path["b.patch"][2], "defer")
        self.assertEqual(by_path["c.patch"][1], "new")
        self.assertEqual(by_path["c.patch"][2], ps.DEFAULT_VERDICT)
        self.assertEqual(by_path["removed.patch"][1], "removed")

    def test_empty_baseline_all_new(self):
        rows = ps.diff_against_baseline({"x": "h"}, {})
        self.assertEqual(rows, [("x", "new", ps.DEFAULT_VERDICT, "")])


class BaselineIOTests(unittest.TestCase):
    def test_save_stable_order(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "baseline.json"
            ps.save_baseline(path, {"sources": {
                "z": {"b.patch": {"sha256": "1"},
                      "a.patch": {"sha256": "2"}},
                "a": {"x.patch": {"sha256": "3"}},
            }})
            loaded = json.loads(path.read_text())
            self.assertEqual(list(loaded["sources"]), ["a", "z"])
            self.assertEqual(
                list(loaded["sources"]["z"]),
                ["a.patch", "b.patch"],
            )

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                ps.load_baseline(Path(td) / "missing.json"),
                {"sources": {}},
            )


if __name__ == "__main__":
    unittest.main()
