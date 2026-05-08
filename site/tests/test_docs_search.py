import json
import subprocess
import sys
import unittest
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = SITE_ROOT / "dist"
DOCS_HOME = DIST_DIR / "docs" / "index.html"
SEARCH_INDEX = DIST_DIR / "docs" / "assets" / "search-index.json"


class DocsSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, "src/build.py"], cwd=SITE_ROOT, check=True)
        cls.index = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))

    def test_docs_shell_includes_search_ui_assets(self) -> None:
        html = DOCS_HOME.read_text(encoding="utf-8")
        self.assertIn("docs-search.css", html)
        self.assertIn("docs-search.js", html)
        self.assertIn('data-docs-search-open', html)
        self.assertIn('id="docs-search-modal"', html)

    def test_search_index_covers_representative_doc_locations(self) -> None:
        indexed_urls = {entry["url"] for entry in self.index}
        self.assertIn("/docs/", indexed_urls)
        self.assertIn("/docs/concepts/#schema-writing-guide", indexed_urls)
        self.assertIn("/docs/learn-by-example/#00-installation", indexed_urls)
        self.assertIn("/docs/lib-and-sdk-survey/#cli", indexed_urls)
        self.assertIn("/docs/examples/full-stack/#layout", indexed_urls)

    def test_search_index_entries_include_prose_snippets(self) -> None:
        entries_by_url = {entry["url"]: entry for entry in self.index}
        installation = entries_by_url["/docs/learn-by-example/#00-installation"]
        cli = entries_by_url["/docs/lib-and-sdk-survey/#cli"]
        self.assertGreater(len(installation["text"]), 40)
        self.assertIn("Installation", installation["title"])
        self.assertGreater(len(cli["text"]), 40)
        self.assertEqual("CLI", cli["title"])


if __name__ == "__main__":
    unittest.main()
