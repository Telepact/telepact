#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "site"
DIST_DOCS_DIR = SITE_ROOT / "dist" / "docs"
SEARCH_INDEX_PATH = DIST_DOCS_DIR / "assets" / "search-index.json"
DOCS_CSS_PATH = DIST_DOCS_DIR / "assets" / "docs.css"
DOCS_INDEX_PATH = DIST_DOCS_DIR / "index.html"
DOCS_SEARCH_SCRIPT_PATH = DIST_DOCS_DIR / "assets" / "docs-search.js"


def normalize_docs_path(value: str) -> str:
    """Return a docs path without any in-page anchor fragment."""
    return value.split("#", 1)[0] or "./"


def run_search_client(entries: list[dict[str, str]], current_href: str, query: str) -> dict[str, object]:
    """Execute the built docs search client under Node and return its rendered result state."""
    node_script = r"""
const fs = require("fs");
const vm = require("vm");

const [scriptPath, currentHref, query] = process.argv.slice(1);
const entries = JSON.parse(fs.readFileSync(0, "utf8"));

function createElement() {
  return {
    hidden: false,
    textContent: "",
    innerHTML: "",
    value: "",
    listeners: {},
    focus() {},
    select() {},
    querySelector() {
      return null;
    },
    addEventListener(type, handler) {
      this.listeners[type] = handler;
    },
  };
}

const modal = createElement();
modal.hidden = true;
const openButton = createElement();
const closeButton = createElement();
const input = createElement();
const results = createElement();
results.hidden = true;
const status = createElement();
const shortcut = createElement();

const document = {
  baseURI: "https://example.test/docs/",
  currentScript: {
    src: "https://example.test/docs/assets/docs-search.js",
    dataset: {
      docsSearchIndex: "https://example.test/docs/assets/search-index.json",
    },
  },
  body: {
    classList: {
      add() {},
      remove() {},
    },
  },
  listeners: {},
  querySelector(selector) {
    switch (selector) {
      case "[data-docs-search-modal]":
        return modal;
      case "[data-docs-search-input]":
        return input;
      case "[data-docs-search-results]":
        return results;
      case "[data-docs-search-status]":
        return status;
      case "[data-docs-search-shortcut]":
        return shortcut;
      default:
        return null;
    }
  },
  querySelectorAll(selector) {
    switch (selector) {
      case "[data-docs-search-open]":
        return [openButton];
      case "[data-docs-search-close]":
        return [closeButton];
      default:
        return [];
    }
  },
  addEventListener(type, handler) {
    this.listeners[type] = handler;
  },
};

const context = {
  console,
  document,
  window: {
    document,
    location: { href: currentHref },
    requestAnimationFrame(callback) {
      callback();
    },
  },
  navigator: { platform: "Linux" },
  URL,
  fetch: async () => ({
    ok: true,
    async json() {
      return entries;
    },
  }),
  Promise,
  setTimeout,
  clearTimeout,
};

vm.createContext(context);
vm.runInContext(fs.readFileSync(scriptPath, "utf8"), context);

(async () => {
  await Promise.resolve();
  await Promise.resolve();
  openButton.listeners.click({});
  await Promise.resolve();
  await Promise.resolve();
  input.value = query;
  input.listeners.input({});
  await Promise.resolve();
  const hrefs = Array.from(results.innerHTML.matchAll(/href="([^"]+)"/g), (match) => match[1]);
  process.stdout.write(JSON.stringify({
    status: status.textContent,
    modalHidden: modal.hidden,
    resultsHidden: results.hidden,
    hrefs,
  }));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""

    completed = subprocess.run(
        ["node", "-e", node_script, str(DOCS_SEARCH_SCRIPT_PATH), current_href, query],
        input=json.dumps(entries),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


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

        self.assertTrue(
            any(
                normalize_docs_path(entry["path"]) == "lib-and-sdk-survey/"
                and entry["section"].startswith("Python")
                for entry in self.entries
            ),
            "Expected Python survey content to be indexed in lib-and-sdk-survey/",
        )

    def test_modal_hidden_state_is_preserved_in_built_assets(self) -> None:
        html = DOCS_INDEX_PATH.read_text(encoding="utf-8")
        css = DOCS_CSS_PATH.read_text(encoding="utf-8")

        self.assertIn('class="docs-search-modal" data-docs-search-modal hidden', html)
        self.assertIn(".docs-search-modal[hidden]", css)
        self.assertIn(".docs-search-results[hidden]", css)
        self.assertRegex(css, re.compile(r"\.docs-search-modal\s*\{[^}]*overflow-y:\s*auto;", re.DOTALL))
        self.assertRegex(css, re.compile(r"\.docs-search-dialog\s*\{[^}]*display:\s*flex;[^}]*flex-direction:\s*column;", re.DOTALL))
        self.assertRegex(css, re.compile(r"\.docs-search-body\s*\{[^}]*display:\s*flex;[^}]*min-height:\s*0;[^}]*overflow:\s*hidden;", re.DOTALL))
        self.assertRegex(css, re.compile(r"\.docs-search-results\s*\{[^}]*flex:\s*1 1 auto;[^}]*min-height:\s*0;[^}]*overflow-y:\s*auto;", re.DOTALL))
        self.assertRegex(css, re.compile(r"\.docs-article h1,\s*\.docs-article h2,\s*\.docs-article h3,\s*\.docs-article h4,\s*\.docs-article h5,\s*\.docs-article h6\s*\{[^}]*scroll-margin-top:\s*96px;", re.DOTALL))

    def test_search_client_excludes_current_document_and_sorts_doc_types(self) -> None:
        results = run_search_client(
            [
                {
                    "title": "Concepts",
                    "section": "Concepts",
                    "path": "concepts/#overview",
                    "content": "alpha topic",
                    "searchText": "concepts alpha topic",
                },
                {
                    "title": "Overview",
                    "section": "Overview",
                    "path": "./#intro",
                    "content": "alpha topic",
                    "searchText": "overview alpha topic",
                },
                {
                    "title": "Survey",
                    "section": "Survey",
                    "path": "lib-and-sdk-survey/#alpha",
                    "content": "alpha topic",
                    "searchText": "survey alpha topic",
                },
                {
                    "title": "Example",
                    "section": "Example",
                    "path": "examples/full-stack/#alpha",
                    "content": "alpha topic",
                    "searchText": "example alpha topic",
                },
            ],
            "https://example.test/docs/",
            "alpha",
        )

        self.assertEqual(results["status"], "3 results")
        self.assertFalse(results["modalHidden"])
        self.assertFalse(results["resultsHidden"])
        self.assertEqual(
            results["hrefs"],
            [
                "https://example.test/docs/concepts/#overview",
                "https://example.test/docs/lib-and-sdk-survey/#alpha",
                "https://example.test/docs/examples/full-stack/#alpha",
            ],
        )

    def test_search_client_caps_results_at_fifty(self) -> None:
        results = run_search_client(
            [
                {
                    "title": f"Guide {index}",
                    "section": "Guide",
                    "path": f"concepts/#guide-{index}",
                    "content": "guide topic",
                    "searchText": f"guide {index} topic",
                }
                for index in range(60)
            ],
            "https://example.test/docs/",
            "guide",
        )

        self.assertEqual(results["status"], "50 results")
        self.assertEqual(len(results["hrefs"]), 50)
        self.assertEqual(results["hrefs"][0], "https://example.test/docs/concepts/#guide-0")
        self.assertEqual(len(set(results["hrefs"])), 50)
