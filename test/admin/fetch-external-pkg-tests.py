#!/usr/bin/env python3
"""Unit tests for admin/fetch-external-pkg and admin/external-packages.json.

Run with:
    python3 test/admin/fetch-external-pkg-tests.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Paths relative to the Emacs repository root.
REPO_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "admin" / "external-packages.json"
SCRIPT_PATH = REPO_ROOT / "admin" / "fetch-external-pkg"

REQUIRED_PACKAGES = {"tramp", "org", "eglot", "erc", "gnus"}


def _import_script():
    """Import admin/fetch-external-pkg as a Python module.

    spec_from_file_location returns None for extension-less files because
    no loader claims them automatically.  Supply SourceFileLoader explicitly.
    """
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("fetch_external_pkg", str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader("fetch_external_pkg", loader,
                                           origin=str(SCRIPT_PATH))
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class ManifestTests(unittest.TestCase):
    """Tests for admin/external-packages.json."""

    def _load(self):
        with open(MANIFEST_PATH) as f:
            return json.load(f)

    def test_manifest_file_exists(self):
        self.assertTrue(MANIFEST_PATH.exists(),
                        f"admin/external-packages.json not found at {MANIFEST_PATH}")

    def test_manifest_valid_json(self):
        data = self._load()
        self.assertIsInstance(data, dict)
        self.assertIn("packages", data)

    def test_required_packages_present(self):
        data = self._load()
        packages = set(data.get("packages", {}).keys())
        missing = REQUIRED_PACKAGES - packages
        self.assertFalse(
            missing,
            f"Manifest missing required packages: {sorted(missing)}"
        )

    def test_each_package_has_paths_list(self):
        data = self._load()
        for name, pkg in data["packages"].items():
            with self.subTest(package=name):
                self.assertIn("paths", pkg, f"{name}: missing 'paths' key")
                self.assertIsInstance(
                    pkg["paths"], list, f"{name}: 'paths' must be a list"
                )

    def test_packages_with_upstream_have_valid_url(self):
        data = self._load()
        for name, pkg in data["packages"].items():
            url = pkg.get("upstream_url")
            if url is not None:
                with self.subTest(package=name):
                    self.assertRegex(
                        url,
                        r"^https?://",
                        f"{name}: 'upstream_url' must start with http(s)://"
                    )

    def test_path_entries_have_from_and_to(self):
        data = self._load()
        for name, pkg in data["packages"].items():
            for i, entry in enumerate(pkg.get("paths", [])):
                with self.subTest(package=name, entry_index=i):
                    self.assertIn(
                        "from", entry,
                        f"{name}[{i}]: path entry missing 'from'"
                    )
                    self.assertIn(
                        "to", entry,
                        f"{name}[{i}]: path entry missing 'to'"
                    )


class ScriptImportTests(unittest.TestCase):
    """Tests that admin/fetch-external-pkg can be imported as a module."""

    def test_script_file_exists(self):
        self.assertTrue(SCRIPT_PATH.exists(),
                        f"admin/fetch-external-pkg not found at {SCRIPT_PATH}")

    def test_script_exposes_load_manifest(self):
        mod = _import_script()
        self.assertTrue(
            hasattr(mod, "load_manifest"),
            "Script must expose a load_manifest() function"
        )

    def test_script_exposes_resolve_package(self):
        mod = _import_script()
        self.assertTrue(
            hasattr(mod, "resolve_package"),
            "Script must expose a resolve_package() function"
        )

    def test_load_manifest_returns_dict(self):
        mod = _import_script()
        data = mod.load_manifest(MANIFEST_PATH)
        self.assertIsInstance(data, dict)
        self.assertIn("packages", data)

    def test_resolve_package_tramp(self):
        mod = _import_script()
        data = mod.load_manifest(MANIFEST_PATH)
        pkg = mod.resolve_package(data, "tramp")
        self.assertIsNotNone(pkg)
        self.assertIn("upstream_url", pkg)
        self.assertIn("paths", pkg)

    def test_resolve_unknown_package_exits(self):
        mod = _import_script()
        data = mod.load_manifest(MANIFEST_PATH)
        with self.assertRaises(SystemExit):
            mod.resolve_package(data, "no-such-package-xyz-999")

    def test_resolve_package_without_upstream_is_allowed(self):
        """Packages like ERC with no separate upstream are valid."""
        mod = _import_script()
        data = mod.load_manifest(MANIFEST_PATH)
        pkg = mod.resolve_package(data, "erc")
        self.assertIsNotNone(pkg)


class CopyFilesTests(unittest.TestCase):
    """Tests for the file-copy helper in admin/fetch-external-pkg."""

    def test_copy_files_transfers_matching_files(self):
        mod = _import_script()
        with tempfile.TemporaryDirectory() as src_td, \
             tempfile.TemporaryDirectory() as dst_td:
            src = Path(src_td)
            dst = Path(dst_td)

            # Create a fake upstream file.
            fake = src / "lisp" / "tramp.el"
            fake.parent.mkdir(parents=True)
            fake.write_text(";; fake tramp\n")

            paths = [{"from": "lisp/tramp.el", "to": "lisp/net/"}]
            mod.copy_files(src, dst, paths)

            out = dst / "lisp" / "net" / "tramp.el"
            self.assertTrue(out.exists(), f"Expected {out} to exist after copy_files")
            self.assertEqual(out.read_text(), ";; fake tramp\n")

    def test_copy_files_glob_pattern(self):
        mod = _import_script()
        with tempfile.TemporaryDirectory() as src_td, \
             tempfile.TemporaryDirectory() as dst_td:
            src = Path(src_td)
            dst = Path(dst_td)

            lisp = src / "lisp"
            lisp.mkdir()
            (lisp / "tramp.el").write_text(";; tramp\n")
            (lisp / "tramp-sh.el").write_text(";; tramp-sh\n")
            (lisp / "other.el").write_text(";; other\n")

            paths = [{"from": "lisp/tramp*.el", "to": "lisp/net/"}]
            mod.copy_files(src, dst, paths)

            net = dst / "lisp" / "net"
            self.assertTrue((net / "tramp.el").exists())
            self.assertTrue((net / "tramp-sh.el").exists())
            self.assertFalse((net / "other.el").exists())


if __name__ == "__main__":
    unittest.main()
