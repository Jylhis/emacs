#!/usr/bin/env python3
"""Synthetic-fixture unit tests for classify.py.

Run from the skill directory:

    python3 -m unittest scripts/test_classify.py
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

import classify  # noqa: E402  (module-style import after sys.path)


def commit(sha: str, subject: str, files: list[str], lines: int = 5,
           missing: bool = False) -> classify.Commit:
    c = classify.Commit(sha=sha, subject=subject, files=files, lines=lines)
    return c


class ClassifyTests(unittest.TestCase):

    # ---- SKIP rules ---------------------------------------------------------

    def test_autotools_skip(self):
        for files in [
            ["configure.ac"],
            ["src/Makefile.in"],
            ["m4/foo.m4"],
            ["GNUmakefile"],
            ["autogen.sh"],
        ]:
            with self.subTest(files=files), \
                 patch.object(os.path, "exists", return_value=True):
                d = classify.classify(commit("a" * 40, "anything", files))
                self.assertEqual(d.bucket, "autotools")

    def test_merge_noise_skip(self):
        with patch.object(os.path, "exists", return_value=True):
            for subj in [
                "Merge from origin/emacs-31",
                "; Merge from emacs-31",
                "Sync with master via gitmerge",
            ]:
                with self.subTest(subj=subj):
                    d = classify.classify(
                        commit("a" * 40, subj, ["lisp/foo.el"]))
                    self.assertEqual(d.bucket, "merge-noise")

    def test_admin_skip_includes_changelog(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "; Update ChangeLog.4", ["ChangeLog.4"]))
            self.assertEqual(d.bucket, "admin")

    def test_admin_skip_includes_maintainers(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Mark myself as maintainer", ["etc/MAINTAINERS"]))
            self.assertEqual(d.bucket, "admin")

    # ---- Missing-file forces REVIEW ----------------------------------------

    def test_missing_file_forces_review(self):
        # Forge a commit that would otherwise be lisp-doc-style AUTO.
        c = commit("a" * 40, "; foo: Improve docstring",
                   ["lisp/textmodes/markdown-ts-mode-x.el"], lines=5)
        with patch.object(os.path, "exists", return_value=False):
            d = classify.classify(c)
            self.assertEqual(d.bucket, "review")
            self.assertTrue(d.reason.startswith("missing-file:"))

    # ---- AUTO doc-only ------------------------------------------------------

    def test_doc_only_news_31(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "; etc/NEWS: Fix typo", ["etc/NEWS.31"]))
            self.assertEqual(d.bucket, "doc-only")

    def test_doc_only_upstream_news_alias(self):
        c = commit("a" * 40, "; etc/NEWS: Fix typo", ["etc/NEWS"])
        with patch.object(os.path, "exists",
                          side_effect=lambda p: p != "etc/NEWS"), \
             patch.object(classify.glob, "glob", return_value=["etc/NEWS.31"]):
            d = classify.classify(c)
            self.assertEqual(d.bucket, "doc-only")

    def test_doc_only_authors(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "; Update etc/AUTHORS", ["etc/AUTHORS"]))
            self.assertEqual(d.bucket, "doc-only")

    def test_doc_only_texi(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Improve docs", ["doc/lispref/foo.texi"]))
            self.assertEqual(d.bucket, "doc-only")

    # ---- AUTO test-only -----------------------------------------------------

    def test_test_only(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Add ERT coverage",
                ["test/lisp/foo-tests.el"]))
            self.assertEqual(d.bucket, "test-only")

    # ---- AUTO lisp bugfix ---------------------------------------------------

    def test_lisp_bugfix(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Fix indent (Bug#80909)",
                ["lisp/treesit.el", "test/lisp/treesit-tests.el"]))
            self.assertEqual(d.bucket, "lisp-bugfix")

    # ---- AUTO lisp doc-or-style fix ----------------------------------------

    def test_lisp_doc_style_semicolon(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "; treesit-ready-p: Fix docstring",
                ["lisp/treesit.el"], lines=4))
            self.assertEqual(d.bucket, "lisp-doc-style")

    def test_lisp_doc_style_keyword(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40,
                "lisp/emacs-lisp/crm.el (crm-complete-and-exit): "
                "Simplify docstring",
                ["lisp/emacs-lisp/crm.el"], lines=14))
            self.assertEqual(d.bucket, "lisp-doc-style")

    def test_lisp_doc_style_too_many_lines(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "; foo: Improve docstring",
                ["lisp/foo.el"], lines=80))
            # Falls through to REVIEW since we required < 50 lines.
            self.assertEqual(d.bucket, "review")

    # ---- AUTO small src fix -------------------------------------------------

    def test_small_src_pacify(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Pacify -Wunused-but-set-variable from gcc 16",
                ["src/coding.c"], lines=26))
            self.assertEqual(d.bucket, "small-src")

    def test_small_src_under_20_no_bug(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Refactor xfns.c symbol naming",
                ["src/xfns.c"], lines=2))
            self.assertEqual(d.bucket, "small-src")

    def test_small_src_too_big(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Big rework of display engine",
                ["src/xdisp.c"], lines=80))
            # Falls through to REVIEW.
            self.assertEqual(d.bucket, "review")

    # ---- AUTO lisp+NEWS Bug# ------------------------------------------------

    def test_lisp_news_bug(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40,
                "Eglot: find well behaved UTF char (bug#80326)",
                ["lisp/progmodes/eglot.el", "etc/NEWS.31"], lines=10))
            self.assertEqual(d.bucket, "lisp+news-bug")

    # ---- REVIEW: feature subject -------------------------------------------

    def test_feature_review(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Add new context-menu-send-to command",
                ["lisp/mouse.el", "lisp/send-to.el"], lines=29))
            self.assertEqual(d.bucket, "review")
            self.assertEqual(d.reason, "feature")

    def test_introduce_feature_review(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Introduce 'margin' face for window margin",
                ["lisp/faces.el", "src/xdisp.c"], lines=235))
            self.assertEqual(d.bucket, "review")
            # Ordering: feature wins over `large`.
            self.assertEqual(d.reason, "feature")


if __name__ == "__main__":
    unittest.main()
