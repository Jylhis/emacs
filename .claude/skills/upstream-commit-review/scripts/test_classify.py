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
           missing: bool = False, body: str = "",
           added_files: set[str] | None = None) -> classify.Commit:
    c = classify.Commit(
        sha=sha,
        subject=subject,
        body=body,
        files=files,
        added_files=added_files or set(),
        lines=lines,
    )
    return c


class ClassifyTests(unittest.TestCase):

    # ---- SKIP rules ---------------------------------------------------------

    def test_autotools_skip(self):
        for files in [
            ["configure.ac"],
            ["src/Makefile.in"],
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

    # ---- Removed-area SKIP --------------------------------------------------

    def test_removed_area_all_lwlib_is_skipped(self):
        c = commit("b" * 40, "Avoid a memset in lwlib", ["lwlib/lwlib.c"])
        d = classify.classify(c)
        self.assertEqual(d.bucket, "removed-area")

    def test_removed_area_msdos_only_is_skipped(self):
        c = commit("c" * 40, "Fix the MSDOS build",
                   ["msdos/sedlibmk.inp", "config.bat"])
        d = classify.classify(c)
        self.assertEqual(d.bucket, "removed-area")

    def test_removed_area_m4_only_is_skipped(self):
        c = commit("d" * 40, "Fix overquoting in gl_SET_MAKEINFO",
                   ["m4/texinfo.m4"])
        d = classify.classify(c)
        self.assertEqual(d.bucket, "removed-area")

    def test_removed_area_w32proc_only_is_skipped(self):
        c = commit("e" * 40,
                   "Improve w32 implementations of 'signal' and 'raise'",
                   ["src/w32proc.c"])
        d = classify.classify(c)
        self.assertEqual(d.bucket, "removed-area")

    def test_removed_area_haiku_only_is_skipped(self):
        c = commit("f" * 40, "Avoid memsets in haiku front-end",
                   ["src/haikufns.c", "src/haikuterm.c"])
        d = classify.classify(c)
        self.assertEqual(d.bucket, "removed-area")

    def test_removed_area_mixed_still_reviews(self):
        # Commit touches a removed file AND a file we still ship; the
        # missing-file rule should still fire (so the human decides
        # whether the non-removed portion is worth a partial apply).
        c = commit("a" * 40, "Cross-area cleanup",
                   ["lwlib/lwlib.c", "src/process.c"])
        with patch.object(os.path, "exists",
                          side_effect=lambda p: p == "src/process.c"):
            d = classify.classify(c)
            self.assertEqual(d.bucket, "review")
            self.assertTrue(d.reason.startswith("missing-file:"))

    def test_removed_area_translations_skips_non_en(self):
        c = commit("a" * 40, "; fr: Fix typos",
                   ["doc/translations/fr/info_common.mk"])
        d = classify.classify(c)
        self.assertEqual(d.bucket, "removed-area")

    def test_removed_area_translations_en_still_applies(self):
        # The English translation IS shipped — don't skip those.
        with patch.object(os.path, "exists", return_value=True):
            c = commit("a" * 40, "; en: Improve doc",
                       ["doc/translations/en/info_common.mk"])
            d = classify.classify(c)
            self.assertNotEqual(d.bucket, "removed-area")

    # ---- AUTO doc-only ------------------------------------------------------

    def test_doc_only_news_31(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "; etc/NEWS: Fix typo", ["etc/NEWS.31"]))
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

    # ---- Bug# matched in body (not subject) --------------------------------

    def test_lisp_bugfix_bug_in_body(self):
        """`c68f3237bea2` shape: Bug# only in body, subject doesn't say."""
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Fix file-name-non-special impl of get-file-buffer",
                ["lisp/files.el", "test/lisp/files-tests.el"],
                lines=18,
                body=("* lisp/files.el (file-name-non-special): "
                      "Fix `get-file-buffer'.  (Bug#80718)")))
            self.assertEqual(d.bucket, "lisp-bugfix")

    def test_small_src_bug_in_body(self):
        with patch.object(os.path, "exists", return_value=True):
            d = classify.classify(commit(
                "a" * 40, "Tweak compositor",
                ["src/composite.c"], lines=30,
                body="Tighten the loop, see Bug#80999."))
            self.assertEqual(d.bucket, "small-src")

    # ---- etc/NEWS rename: not flagged as missing-file ----------------------

    def test_etc_news_routes_to_news_31(self):
        """`984024daf3ce` shape: commit touches upstream etc/NEWS; the
        fork has etc/NEWS.31 instead.  Should not be demoted on missing."""
        def fake_exists(p: str) -> bool:
            return p == "etc/NEWS.31" or p.startswith(("lisp/", "doc/"))
        with patch.object(os.path, "exists", side_effect=fake_exists):
            d = classify.classify(commit(
                "a" * 40, "Eglot: rendering tweak (bug#80127)",
                ["lisp/progmodes/eglot.el", "doc/misc/eglot.texi",
                 "etc/NEWS"], lines=12))
            self.assertEqual(d.bucket, "lisp+news-bug")

    # ---- Added files: not flagged missing ----------------------------------

    def test_added_file_is_not_missing(self):
        """`cf9728c4be8f` shape: commit creates a new test scenario file."""
        def fake_exists(p: str) -> bool:
            return p != "test/lisp/erc/erc-scenarios-log-options.el"
        with patch.object(os.path, "exists", side_effect=fake_exists):
            d = classify.classify(commit(
                "a" * 40, "Only perform erc-log-insert-log-on-open setup once",
                ["lisp/erc/erc-log.el", "etc/ERC-NEWS",
                 "test/lisp/erc/erc-scenarios-log-options.el"],
                lines=316,
                added_files={"test/lisp/erc/erc-scenarios-log-options.el"}))
            # Large but should land in REVIEW for size, not missing-file.
            self.assertEqual(d.bucket, "review")
            self.assertEqual(d.reason, "large")

    # ---- Release-branch detection ------------------------------------------

    def test_release_branch_skip(self):
        with patch.object(os.path, "exists", return_value=True):
            for subj in [
                "Change ERC version for Emacs 31 to 5.6.2.31.1",
                "Cut the emacs-31 release branch",
                "Bump master Emacs version to 32.0.50",
            ]:
                with self.subTest(subj=subj):
                    d = classify.classify(commit(
                        "a" * 40, subj, ["lisp/erc/erc.el"]))
                    self.assertEqual(d.bucket, "release-branch")


if __name__ == "__main__":
    unittest.main()
