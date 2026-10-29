"""The package imports, says what it is, and its versions map to one tag."""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
spec = importlib.util.spec_from_file_location("version", ROOT / "scripts" / "version.py")
version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version)

import figpress_plotly  # noqa: E402


class PackageTest(unittest.TestCase):
    def test_version_and_status(self):
        self.assertRegex(figpress_plotly.__version__, r"^\d{4}\.\d{2}\.\d{2}(\.\d+)?$")
        self.assertIn("early development", figpress_plotly.__doc__)

    def test_versions_map_to_one_tag(self):
        have = version.current()
        self.assertEqual(have, version.versions(f"v{have['pypi']}"))

    def test_tag_mapping(self):
        self.assertEqual(version.versions("v2026.10.28.2"), {"pypi": "2026.10.28.2", "npm": "20261028.0.2"})


if __name__ == "__main__":
    unittest.main()
