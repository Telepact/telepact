from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "site"
DIST_DOCS_DIR = SITE_ROOT / "dist" / "docs"
SEARCH_INDEX_PATH = DIST_DOCS_DIR / "assets" / "search-index.json"


def normalize_docs_path(value: str) -> str:
    return value.split("#", 1)[0] or "./"


class DocsSearchIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, str(SITE_ROOT / "src" / "build.py")],
            cwd=SITE_ROOT,
            check=True,
        )
        cls.entries = json.loads(SEARCH_INDEX_PATH.read_text(encoding="utf-8"))

    def test_every_generated_doc_page_has_search_entries(self) -> None:
        expected_paths = {
            path.relative_to(DIST_DOCS_DIR).as_posix()[: -len("index.html")] or "./"
            for path in DIST_DOCS_DIR.rglob("index.html")
        }
        indexed_paths = {normalize_docs_path(entry["path"]) for entry in self.entries}
        self.assertTrue(
            expected_paths.issubset(indexed_paths),
            f"Missing indexed docs paths: {sorted(expected_paths - indexed_paths)}",
        )

    def test_search_index_covers_sampled_doc_locations(self) -> None:
        sampled_expectations = [
            ("./", "Welcome to the Telepact docs"),
            ("concepts/", "minimum Telepact API ecosystem"),
            ("learn-by-example/", "Let's learn Telepact the same way we'll use it in real life"),
            ("examples/", "Runnable end-to-end demos live here"),
            ("examples/full-stack/", "production-boundary concerns"),
            ("lib-and-sdk-survey/", "Telepact Library for Python"),
        ]

        for expected_path, expected_phrase in sampled_expectations:
            self.assertTrue(
                any(
                    normalize_docs_path(entry["path"]) == expected_path
                    and expected_phrase.lower() in entry["content"].lower()
                    for entry in self.entries
                ),
                f"Expected search entry for {expected_path!r} containing {expected_phrase!r}",
            )
