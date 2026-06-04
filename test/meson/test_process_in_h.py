"""Tests for meson/process_in_h.py gnulib header post-processing transforms."""

import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "meson"))
from process_in_h import _append_assert_static_assert, _rewrite_ieee754_guard


class TestRewriteIeee754Guard(unittest.TestCase):
    def test_replaces_first_occurrence(self):
        text = "#ifndef _GL_GNULIB_HEADER\n/* body */\n#endif\n"
        result = _rewrite_ieee754_guard(text)
        self.assertIn("#if 0", result)
        self.assertNotIn("#ifndef _GL_GNULIB_HEADER", result)

    def test_replaces_only_first_occurrence(self):
        text = (
            "#ifndef _GL_GNULIB_HEADER\nfirst\n"
            "#ifndef _GL_GNULIB_HEADER\nsecond\n"
        )
        result = _rewrite_ieee754_guard(text)
        self.assertEqual(result.count("#if 0"), 1)
        self.assertEqual(result.count("#ifndef _GL_GNULIB_HEADER"), 1)

    def test_unchanged_when_pattern_absent(self):
        text = "#ifndef _SOME_OTHER_GUARD\n#endif\n"
        self.assertEqual(_rewrite_ieee754_guard(text), text)

    def test_against_actual_ieee754_in_h(self):
        src = Path(__file__).parent.parent.parent / "lib" / "ieee754.in.h"
        if not src.exists():
            self.skipTest("lib/ieee754.in.h not found")
        text = src.read_text()
        result = _rewrite_ieee754_guard(text)
        self.assertNotIn("#ifndef _GL_GNULIB_HEADER", result)
        self.assertIn("#if 0", result)
        # Outer _IEEE754_H guard must be untouched.
        self.assertIn("#ifndef _IEEE754_H", result)


class TestAppendAssertStaticAssert(unittest.TestCase):
    LIB = Path(__file__).parent.parent.parent / "lib"

    def setUp(self):
        if not self.LIB.exists():
            self.skipTest("lib/ directory not found")
        if not (self.LIB / "verify.h").exists():
            self.skipTest("lib/verify.h not found")

    def _run(self, base: str = "/* base */\n") -> str:
        return _append_assert_static_assert(base, self.LIB)

    def test_appends_content(self):
        result = self._run()
        self.assertGreater(len(result), len("/* base */\n"))

    def test_omit_section_is_stripped(self):
        result = self._run()
        # The assume/builtin-trap block should not appear in the output.
        self.assertNotIn("/* @assert.h omit start@", result)
        self.assertNotIn("/* @assert.h omit end@", result)
        self.assertNotIn("_GL_HAS_BUILTIN_TRAP", result)
        self.assertNotIn("assume(R)", result)

    def test_verify_renamed_to_static_assert(self):
        result = self._run()
        # Lower-case rename.
        self.assertNotIn("_gl_verify", result)
        self.assertIn("_gl_static_assert", result)
        # Upper-case rename (guard becomes _GL_STATIC_ASSERT_H).
        self.assertNotIn("_GL_VERIFY_H", result)
        self.assertIn("_GL_STATIC_ASSERT_H", result)

    def test_no_dead_gl_static_assert_h_function_syntax(self):
        # Regression: ensure the dead-code regex _GL(_STATIC_ASSERT_H) is gone.
        result = self._run()
        import re
        self.assertEqual(
            len(re.findall(r"_GL\(_STATIC_ASSERT_H\)", result)), 0
        )

    def test_against_actual_assert_in_h(self):
        src = self.LIB / "assert.in.h"
        if not src.exists():
            self.skipTest("lib/assert.in.h not found")
        base = src.read_text()
        result = _append_assert_static_assert(base, self.LIB)
        # Omit section absent.
        self.assertNotIn("_GL_HAS_BUILTIN_TRAP", result)
        # Renamed guard present.
        self.assertIn("_GL_STATIC_ASSERT_H", result)


if __name__ == "__main__":
    unittest.main()
