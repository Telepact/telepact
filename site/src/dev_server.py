#!/usr/bin/env python3

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

import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


SITE_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = SITE_ROOT / "dist"
PORT = int(os.environ.get("PORT", "3000"))


class MarkdownNegotiatingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Vary", "Content-Type")
        super().end_headers()

    def send_head(self):
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() == "text/markdown":
            markdown_path = self.resolve_markdown_variant()
            if markdown_path is not None:
                file_handle = markdown_path.open("rb")
                stats = markdown_path.stat()
                self.send_response(200)
                self.send_header("Content-Type", "text/markdown; charset=utf-8")
                self.send_header("Content-Length", str(stats.st_size))
                self.send_header("Last-Modified", self.date_time_string(stats.st_mtime))
                self.end_headers()
                return file_handle
        return super().send_head()

    def resolve_markdown_variant(self) -> Path | None:
        path = unquote(urlsplit(self.path).path)
        for candidate in self.markdown_candidates(path):
            if candidate.is_file():
                return candidate
        return None

    def markdown_candidates(self, request_path: str) -> list[Path]:
        clean_path = request_path.lstrip("/")
        if not clean_path:
            return [DIST_DIR / "index.md"]

        resolved = DIST_DIR / clean_path
        if request_path.endswith("/"):
            return [resolved / "index.md"]
        if resolved.suffix == ".html":
            return [resolved.with_suffix(".md")]
        if resolved.suffix == ".md":
            return [resolved]
        return [resolved / "index.md", resolved.with_suffix(".md")]


def main() -> None:
    with ThreadingHTTPServer(("0.0.0.0", PORT), MarkdownNegotiatingHandler) as server:
        print(f"Serving {DIST_DIR} on http://0.0.0.0:{PORT}")
        server.serve_forever()


if __name__ == "__main__":
    main()
