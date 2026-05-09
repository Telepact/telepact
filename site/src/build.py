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

import html
import json
import os
import posixpath
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from docs_search import SearchablePage, build_search_index


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "site"
SOURCE_DIR = SITE_ROOT / "src"
SITE_DIR = SITE_ROOT / "dist"
DOCS_DIR = SITE_DIR / "docs"
MARKDOWN_DOCS_DIR = SITE_DIR / "markdown-docs"
GENERATED_SOURCE_DIR = SITE_ROOT / ".generated-docs"
GENERATED_DOCS_SOURCE_DIR = GENERATED_SOURCE_DIR / "docs"
INDEX_TEMPLATE = SOURCE_DIR / "index.template.html"
DOCS_TEMPLATE = SOURCE_DIR / "docs.template.html"
DOCS_CSS_SOURCE = SOURCE_DIR / "docs.css"
DOCS_SEARCH_SCRIPT_SOURCE = SOURCE_DIR / "docs-search.js"
INDEX_OUTPUT = SITE_DIR / "index.html"
LLMS_OUTPUT = SITE_DIR / "llms.txt"
SNIPPETS_DIR = SOURCE_DIR / "snippets"
STATIC_FILES = (".nojekyll", "404.html", "favicon.ico")
DEFAULT_BASE_URL = "https://telepact.github.io/telepact/"
DEFAULT_REPO_URL = "https://github.com/Telepact/telepact"
ALLOWED_PREFIXES = ("doc/", "example/", "lib/", "sdk/", "common/")
PRISM_CSS = (
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/"
    "prism-tomorrow.min.css"
)
PRISM_JS = [
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markup.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-css.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-typescript.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-go.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js",
]
SNIPPET_PATTERN = re.compile(
    r'(?P<indent>[ \t]*)<!--\s*SNIPPET:\s*(?P<path>[^|]+?)\s*\|\s*(?P<lang>[a-zA-Z0-9_-]+)\s*-->'
)
DOCS_PAGE_BLUEPRINTS = (
    {
        "output": "index.md",
        "title": "Documentation",
        "intro": "doc/index.md",
        "sections": (),
    },
    {
        "output": "concepts.md",
        "title": "Concepts",
        "sections": (
            {"source": "doc/example.md"},
            {"source": "doc/design-apis/core-concepts.md"},
            {"source": "doc/design-apis/schema-guide.md"},
            {"source": "doc/design-apis/extensions.md"},
            {"source": "doc/design-apis/select-extension.md"},
            {"source": "doc/design-apis/mock-extensions.md"},
            {"source": "doc/build-clients-and-servers/client-paths.md"},
            {"source": "doc/build-clients-and-servers/server-paths.md"},
            {"source": "doc/build-clients-and-servers/transports.md"},
            {"source": "doc/build-clients-and-servers/auth.md"},
            {"source": "doc/build-clients-and-servers/tooling-workflow.md"},
            {"source": "doc/operate/production-guide.md"},
            {"source": "doc/operate/runtime-errors.md"},
            {"source": "doc/background-and-reference/motivation.md"},
            {"source": "doc/background-and-reference/faq.md"},
        ),
    },
    {
        "output": "learn-by-example.md",
        "title": "Learn by Example",
        "intro": "doc/learn-by-example/README.md",
        "sections": (
            {"source": "doc/learn-by-example/01-getting-started/installation.md"},
            {"source": "doc/learn-by-example/01-getting-started/ping.md"},
            {"source": "doc/learn-by-example/01-getting-started/schema-and-add.md"},
            {"source": "doc/learn-by-example/01-getting-started/data-type-validation.md"},
            {"source": "doc/learn-by-example/02-schema/scalar-types.md"},
            {"source": "doc/learn-by-example/02-schema/collection-types.md"},
            {"source": "doc/learn-by-example/02-schema/structs.md"},
            {"source": "doc/learn-by-example/02-schema/unions.md"},
            {"source": "doc/learn-by-example/02-schema/functions.md"},
            {"source": "doc/learn-by-example/02-schema/service-errors.md"},
            {"source": "doc/learn-by-example/02-schema/headers.md"},
            {"source": "doc/learn-by-example/02-schema/comments.md"},
            {"source": "doc/learn-by-example/03-opt-in-features/select.md"},
            {"source": "doc/learn-by-example/03-opt-in-features/binary.md"},
            {"source": "doc/learn-by-example/04-mocking-an-integration/mock-server.md"},
            {"source": "doc/learn-by-example/04-mocking-an-integration/stock-mock.md"},
            {"source": "doc/learn-by-example/04-mocking-an-integration/stubs.md"},
            {"source": "doc/learn-by-example/04-mocking-an-integration/verify.md"},
            {"source": "doc/learn-by-example/05-auth/auth.md"},
            {"source": "doc/learn-by-example/06-using-telepact-client-library-code/minimum-python-client.md"},
            {"source": "doc/learn-by-example/06-using-telepact-client-library-code/automatic-binary-negotiation.md"},
            {"source": "doc/learn-by-example/07-code-generation/code-generation.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/minimum-server.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/logging.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/server-auth.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/managed-auth.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/schema-evolution.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/test-client-tdd.md"},
            {"source": "doc/learn-by-example/08-running-our-own-server/server-best-practices.md"},
        ),
    },
    {
        "output": "lib-and-sdk-survey.md",
        "title": "Lib and SDK Survey",
        "sections": (
            {"source": "lib/go/README.md", "title": "Go"},
            {"source": "lib/java/README.md", "title": "Java"},
            {"source": "lib/py/README.md", "title": "Python"},
            {"source": "lib/ts/README.md", "title": "TypeScript"},
            {"source": "sdk/cli/README.md", "title": "CLI"},
            {"source": "sdk/console/README.md", "title": "Console"},
            {"source": "sdk/prettier/README.md", "title": "Prettier Plugin"},
        ),
    },
)
INLINE_EXAMPLE_SKIP_NAMES = {"README.md", ".gitignore", "go.sum"}


def normalize_base_url(value: str) -> str:
    value = value.strip()
    if not value:
        return DEFAULT_BASE_URL
    return value.rstrip("/") + "/"


def normalize_domain(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^https?://", "", value)
    return value.strip("/").strip()


CUSTOM_DOMAIN = normalize_domain(os.environ.get("TELEPACT_SITE_CUSTOM_DOMAIN", ""))
DEFAULT_PROJECT_BASE_URL = os.environ.get(
    "TELEPACT_SITE_BASE_URL",
    DEFAULT_BASE_URL,
)
BASE_URL = normalize_base_url(
    f"https://{CUSTOM_DOMAIN}/" if CUSTOM_DOMAIN else DEFAULT_PROJECT_BASE_URL
)
REPO_URL = os.environ.get("TELEPACT_SITE_REPO_URL", DEFAULT_REPO_URL).strip().rstrip("/") or DEFAULT_REPO_URL


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "section"


def strip_markdown(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    return value.strip()


def normalize_lang(lang: str) -> str:
    lang = lang.strip().lower()
    return {
        "py": "python",
        "ts": "typescript",
        "sh": "bash",
        "shell": "bash",
        "yml": "yaml",
    }.get(lang, lang)


def is_external_link(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "tel:"))


def split_link_target(target: str) -> tuple[str, str]:
    if "#" in target:
        path_part, frag = target.split("#", 1)
        return path_part, frag
    return target, ""


def is_allowed_repo_path(path: Path) -> bool:
    if path_in_generated_docs(path):
        return True
    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return False
    return rel.startswith(ALLOWED_PREFIXES)


def repo_rel(path: Path) -> str:
    if path_in_generated_docs(path):
        return path.relative_to(GENERATED_DOCS_SOURCE_DIR).as_posix()
    return path.relative_to(REPO_ROOT).as_posix()


def output_html_path(source: Path) -> Path:
    if path_in_generated_docs(source):
        rel = source.relative_to(GENERATED_DOCS_SOURCE_DIR).as_posix()
        if rel.endswith("/README.md"):
            rel = rel[: -len("README.md")]
        elif rel == "index.md":
            rel = ""
        elif rel.endswith("/index.md"):
            rel = rel[: -len("index.md")]
        elif rel.endswith(".md"):
            rel = rel[:-3] + "/"
        return DOCS_DIR / rel / "index.html"
    rel = repo_rel(source)
    if rel.startswith("doc/"):
        rel = rel[len("doc/") :]
    elif rel.startswith("example/"):
        rel = "examples/" + rel[len("example/") :]
    if rel.endswith("/README.md"):
        rel = rel[: -len("README.md")]
    elif rel == "index.md":
        rel = ""
    elif rel.endswith("/index.md"):
        rel = rel[: -len("index.md")]
    elif rel.endswith(".md"):
        rel = rel[:-3] + "/"
    return DOCS_DIR / rel / "index.html"


def output_resource_path(source: Path) -> Path:
    return DOCS_DIR / repo_rel(source)


def output_markdown_doc_path(source: Path) -> Path:
    return MARKDOWN_DOCS_DIR / source.relative_to(REPO_ROOT / "doc")


def url_from_output(output_file: Path) -> str:
    rel = output_file.relative_to(SITE_DIR).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return rel


def relative_href(from_dir: Path, to_path: Path, trailing_slash: bool = False) -> str:
    rel = os.path.relpath(to_path, from_dir).replace(os.sep, "/")
    if trailing_slash:
        rel = rel[: -len("index.html")] if rel.endswith("index.html") else rel
        if not rel:
            rel = "./"
        elif not rel.endswith("/"):
            rel += "/"
        return rel
    return rel or "."


def resolve_local_target(source: Path, raw_target: str) -> tuple[Path | None, str]:
    path_part, frag = split_link_target(raw_target)
    if not path_part:
        return source, frag
    if is_external_link(path_part):
        return None, frag

    candidate = Path(path_part)
    if candidate.is_absolute():
        resolved = (REPO_ROOT / path_part.lstrip("/")).resolve()
    else:
        resolved = (source.parent / candidate).resolve()

    if not resolved.exists():
        return resolved, frag

    if resolved.is_dir():
        readme = resolved / "README.md"
        index_md = resolved / "index.md"
        if readme.exists():
            resolved = readme
        elif index_md.exists():
            resolved = index_md

    return resolved, frag


def resolve_snippet_path(raw_path: str) -> Path:
    snippet_path = (SNIPPETS_DIR / raw_path.strip()).resolve()
    try:
        snippet_path.relative_to(SNIPPETS_DIR.resolve())
    except ValueError as exc:
        raise ValueError(f"Snippet path escapes site/src/snippets: {raw_path}") from exc
    if not snippet_path.is_file():
        raise FileNotFoundError(f"Missing snippet file: {snippet_path}")
    return snippet_path


def render_snippet(raw_path: str, lang: str) -> str:
    snippet_path = resolve_snippet_path(raw_path)
    snippet_text = snippet_path.read_text(encoding="utf-8").rstrip("\n")
    snippet_html = snippet_text.replace("&", "&amp;").replace("<", "&lt;")
    return f'<pre><code class="language-{lang}">{snippet_html}</code></pre>'


def render_template(template_path: Path, replacements: dict[str, str]) -> str:
    rendered = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def write_home_page() -> int:
    template = INDEX_TEMPLATE.read_text(encoding="utf-8")
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        replacements += 1
        return f'{match.group("indent")}{render_snippet(match.group("path"), match.group("lang"))}'

    rendered = SNIPPET_PATTERN.sub(replace, template)
    rendered = rendered.replace("{{BASE_URL}}", BASE_URL)
    rendered = rendered.replace("{{REPO_URL}}", REPO_URL)
    INDEX_OUTPUT.write_text(rendered, encoding="utf-8")
    return replacements


def copy_static_files() -> None:
    for name in STATIC_FILES:
        shutil.copy2(SOURCE_DIR / name, SITE_DIR / name)


def write_robots() -> None:
    robots = "\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {posixpath.join(BASE_URL.rstrip('/'), 'sitemap.xml')}",
        "",
    ])
    (SITE_DIR / "robots.txt").write_text(robots, encoding="utf-8")


def write_cname() -> None:
    if not CUSTOM_DOMAIN:
        return
    (SITE_DIR / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")


def site_url(path: str) -> str:
    return posixpath.join(BASE_URL.rstrip("/"), path.lstrip("/"))


@dataclass
class Page:
    source: Path
    output_file: Path
    title: str = ""
    summary: str = ""
    toc: list[tuple[int, str, str]] = field(default_factory=list)

    @property
    def rel_source(self) -> str:
        return repo_rel(self.source)

    @property
    def url(self) -> str:
        return url_from_output(self.output_file)


@dataclass(frozen=True)
class NavLink:
    label: str
    target: str


@dataclass(frozen=True)
class NavSubgroup:
    heading: str
    items: list[NavLink]


@dataclass(frozen=True)
class NavGroup:
    heading: str
    items: list[NavLink] = field(default_factory=list)
    subgroups: list[NavSubgroup] = field(default_factory=list)


@dataclass(frozen=True)
class GeneratedSection:
    source: Path
    title: str


@dataclass(frozen=True)
class GeneratedPage:
    output: Path
    title: str
    intro: Path | None = None
    sections: tuple[GeneratedSection, ...] = ()


@dataclass(frozen=True)
class GeneratedTarget:
    output: Path
    anchor: str = ""


ORDERED_NAME_RE = re.compile(r"^(?P<order>\d+)(?:[-_.]|$)(?P<name>.*)$")
TOP_LEVEL_DOC_DIR_ORDER = {
    "design-apis": 2,
    "build-clients-and-servers": 3,
    "operate": 4,
    "background-and-reference": 5,
}
DISPLAY_TOKEN_MAP = {
    "api": "API",
    "apis": "APIs",
    "cli": "CLI",
    "go": "Go",
    "http": "HTTP",
    "https": "HTTPS",
    "json": "JSON",
    "sdk": "SDK",
    "telepact": "Telepact",
    "tdd": "TDD",
    "typescript": "TypeScript",
    "websocket": "WebSocket",
}
LOWERCASE_DISPLAY_TOKENS = {"a", "an", "and", "by", "for", "in", "of", "on", "or", "the", "to", "with"}


def split_ordered_name(name: str) -> tuple[int, str]:
    match = ORDERED_NAME_RE.match(name)
    if match:
        remainder = match.group("name") or name
        return int(match.group("order")), remainder
    return 10**9, name


def sort_nav_paths(paths: list[Path], order_overrides: dict[str, int] | None = None) -> list[Path]:
    def sort_key(path: Path) -> tuple[int, str]:
        raw_name = path.stem if path.is_file() else path.name
        if order_overrides is not None and raw_name in order_overrides:
            return order_overrides[raw_name], raw_name.lower()
        order, remainder = split_ordered_name(raw_name)
        return order, remainder.lower()

    return sorted(
        paths,
        key=sort_key,
    )


def display_name(path: Path) -> str:
    raw_name = path.stem if path.is_file() else path.name
    _, remainder = split_ordered_name(raw_name)
    tokens = [token for token in remainder.split("-") if token]
    if not tokens:
        return remainder or raw_name
    rendered: list[str] = []
    for index, token in enumerate(tokens):
        mapped = DISPLAY_TOKEN_MAP.get(token.lower())
        if mapped is not None:
            rendered.append(mapped)
        elif index > 0 and token.lower() in LOWERCASE_DISPLAY_TOKENS:
            rendered.append(token.lower())
        else:
            rendered.append(token.capitalize())
    return " ".join(rendered)


def path_in_generated_docs(path: Path) -> bool:
    try:
        path.relative_to(GENERATED_DOCS_SOURCE_DIR)
        return True
    except ValueError:
        return False


def page_output_path(output_rel: str) -> Path:
    return GENERATED_DOCS_SOURCE_DIR / output_rel


def relative_posix_path(from_path: Path, to_path: Path) -> str:
    rel = posixpath.relpath(to_path.as_posix(), from_path.parent.as_posix())
    return "." if rel == "." else rel


def first_heading_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if match:
            return strip_markdown(match.group(2).strip()) or fallback
    return fallback


def drop_first_heading(markdown: str) -> tuple[str | None, str]:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if match:
            title = strip_markdown(match.group(2).strip())
            remaining = lines[:index] + lines[index + 1 :]
            return title, "\n".join(remaining).lstrip("\n")
    return None, markdown


def shift_markdown_headings(markdown: str, levels: int) -> str:
    if levels <= 0:
        return markdown
    lines = markdown.splitlines()
    rendered: list[str] = []
    in_code_block = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            rendered.append(line)
            continue
        if not in_code_block:
            match = re.match(r"^(\s*)(#{1,6})(\s+.*)$", line)
            if match:
                hashes = "#" * min(6, len(match.group(2)) + levels)
                rendered.append(f"{match.group(1)}{hashes}{match.group(3)}")
                continue
        rendered.append(line)
    return "\n".join(rendered)


def replace_inline_links(markdown: str, source: Path, current_output: Path, targets: dict[Path, GeneratedTarget]) -> str:
    lines = markdown.splitlines()
    rendered: list[str] = []
    in_code_block = False
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def replace_match(match: re.Match[str]) -> str:
        label, raw_target = match.group(1), match.group(2)
        if is_external_link(raw_target) or raw_target.startswith("#"):
            return match.group(0)

        resolved, frag = resolve_local_target(source, raw_target)
        if resolved is not None and resolved in targets:
            target = targets[resolved]
            rel = relative_posix_path(current_output, target.output)
            if current_output == target.output:
                rel = ""
            anchor = frag or target.anchor
            href = rel
            if anchor:
                href += f"#{anchor}"
            if not href:
                href = "./"
            return f"[{label}]({href})"

        if resolved is not None and resolved.exists() and resolved.is_file() and is_allowed_repo_path(resolved):
            href = "/" + repo_rel(resolved)
            if frag:
                href += f"#{frag}"
            return f"[{label}]({href})"

        return match.group(0)

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            rendered.append(line)
            continue
        if in_code_block:
            rendered.append(line)
            continue
        rendered.append(link_pattern.sub(replace_match, line))
    return "\n".join(rendered)


def example_code_language(path: Path) -> str | None:
    if path.name == "Makefile":
        return "bash"
    if path.name.endswith(".telepact.yaml"):
        return "yaml"
    if path.name.endswith(".telepact.json"):
        return "json"
    if path.suffix == ".py":
        return "python"
    if path.suffix in {".ts", ".tsx"}:
        return "typescript"
    if path.suffix in {".yaml", ".yml"}:
        return "yaml"
    if path.suffix == ".json":
        return "json"
    if path.suffix == ".go":
        return "go"
    if path.suffix == ".java":
        return "java"
    if path.suffix == ".sh":
        return "bash"
    if path.suffix == ".html":
        return "html"
    if path.suffix == ".css":
        return "css"
    return None


def example_source_files(example_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(example_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(example_dir).parts):
            continue
        if path.name in INLINE_EXAMPLE_SKIP_NAMES:
            continue
        files.append(path)
    return files


def generated_pages() -> list[GeneratedPage]:
    pages = [
        GeneratedPage(
            output=page_output_path(blueprint["output"]),
            title=blueprint["title"],
            intro=(REPO_ROOT / blueprint["intro"]) if blueprint.get("intro") else None,
            sections=tuple(
                GeneratedSection(
                    source=REPO_ROOT / section["source"],
                    title=section.get(
                        "title",
                        first_heading_title(
                            (REPO_ROOT / section["source"]).read_text(encoding="utf-8"),
                            display_name(REPO_ROOT / section["source"]),
                        ),
                    ),
                )
                for section in blueprint["sections"]
            ),
        )
        for blueprint in DOCS_PAGE_BLUEPRINTS
    ]

    example_readme = REPO_ROOT / "example" / "README.md"
    pages.append(
        GeneratedPage(
            output=page_output_path("examples.md"),
            title="Examples",
            intro=example_readme,
        )
    )

    for readme in sorted((REPO_ROOT / "example").glob("*/README.md")):
        pages.append(
            GeneratedPage(
                output=page_output_path(f"examples/{readme.parent.name}.md"),
                title=readme.parent.name,
                intro=readme,
            )
        )
    return pages


def generated_targets(pages: list[GeneratedPage]) -> dict[Path, GeneratedTarget]:
    targets: dict[Path, GeneratedTarget] = {}
    for page in pages:
        if page.intro is not None:
            targets[page.intro] = GeneratedTarget(output=page.output)
        for section in page.sections:
            targets[section.source] = GeneratedTarget(output=page.output, anchor=slugify(section.title))

        if page.intro is not None and page.intro.parent.parent == REPO_ROOT / "example":
            example_dir = page.intro.parent
            targets[example_dir] = GeneratedTarget(output=page.output, anchor="source-files")
            for file_path in example_source_files(example_dir):
                rel = file_path.relative_to(example_dir).as_posix()
                anchor = slugify(rel)
                targets[file_path] = GeneratedTarget(output=page.output, anchor=anchor)
                if "/" in rel:
                    top_level = rel.split("/", 1)[0]
                    targets.setdefault(
                        example_dir / top_level,
                        GeneratedTarget(output=page.output, anchor=slugify(top_level)),
                    )
    return targets


def section_markdown(section: GeneratedSection, page_output: Path, targets: dict[Path, GeneratedTarget]) -> str:
    original = section.source.read_text(encoding="utf-8")
    _, body = drop_first_heading(original)
    body = replace_inline_links(body, section.source, page_output, targets)
    body = shift_markdown_headings(body, 1)
    pieces = [f"## {section.title}"]
    if body.strip():
        pieces.append(body.strip())
    return "\n\n".join(pieces).strip()


def example_sources_markdown(example_dir: Path) -> str:
    files = example_source_files(example_dir)
    if not files:
        return ""

    parts = ["## Source Files"]
    current_group: str | None = None
    for file_path in files:
        rel = file_path.relative_to(example_dir).as_posix()
        top_level = rel.split("/", 1)[0] if "/" in rel else None
        if top_level is not None and top_level != current_group:
            current_group = top_level
            parts.append(f"### {top_level}/")
        elif top_level is None:
            current_group = None
        heading_level = "####" if top_level is not None else "###"
        parts.append(f"{heading_level} {rel}")
        lang = example_code_language(file_path)
        if lang is None:
            continue
        code = file_path.read_text(encoding='utf-8').rstrip("\n")
        parts.append(f"```{lang}\n{code}\n```")
    return "\n\n".join(parts)


def write_generated_docs() -> None:
    if GENERATED_SOURCE_DIR.exists():
        shutil.rmtree(GENERATED_SOURCE_DIR)
    GENERATED_DOCS_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    pages = generated_pages()
    targets = generated_targets(pages)

    for page in pages:
        parts = [f"# {page.title}"]
        if page.intro is not None:
            _, intro_body = drop_first_heading(page.intro.read_text(encoding="utf-8"))
            intro_body = replace_inline_links(intro_body, page.intro, page.output, targets).strip()
            if intro_body:
                parts.append(intro_body)
        for section in page.sections:
            parts.append(section_markdown(section, page.output, targets))
        if page.intro is not None and page.intro.parent.parent == REPO_ROOT / "example":
            source_markdown = example_sources_markdown(page.intro.parent)
            if source_markdown:
                parts.append(source_markdown)
        page.output.parent.mkdir(parents=True, exist_ok=True)
        page.output.write_text("\n\n".join(part for part in parts if part).strip() + "\n", encoding="utf-8")


def page_for_source(pages: dict[Path, Page], source: Path) -> Page | None:
    return pages.get(source)


def directory_landing_page(pages: dict[Path, Page], directory: Path) -> Page | None:
    for name in ("README.md", "index.md"):
        page = page_for_source(pages, directory / name)
        if page is not None:
            return page
    return None


def nav_links_for_directory(pages: dict[Path, Page], directory: Path) -> list[NavLink]:
    links: list[NavLink] = []
    landing = directory_landing_page(pages, directory)
    if landing is not None:
        links.append(NavLink(landing.title, landing.rel_source))

    children = [
        child for child in directory.iterdir()
        if child.is_file()
        and child.suffix == ".md"
        and child.name not in {"README.md", "index.md"}
    ]
    for child in sort_nav_paths(children):
        page = page_for_source(pages, child)
        if page is None:
            continue
        links.append(NavLink(page.title, page.rel_source))
    return links


def discover_pages() -> tuple[dict[Path, Page], set[Path]]:
    pages: dict[Path, Page] = {}
    resources: set[Path] = set()
    for source in sorted(GENERATED_DOCS_SOURCE_DIR.rglob("*.md")):
        pages[source] = Page(source=source, output_file=output_html_path(source))
        text = source.read_text(encoding="utf-8")
        for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
            if is_external_link(target):
                continue
            resolved, _ = resolve_local_target(source, target)
            if resolved is None or not resolved.exists() or not resolved.is_file():
                continue
            if resolved.suffix.lower() != ".md" and is_allowed_repo_path(resolved):
                resources.add(resolved)

    return pages, resources


class MarkdownRenderer:
    def __init__(self, page: Page, pages: dict[Path, Page], resources: set[Path]):
        self.page = page
        self.pages = pages
        self.resources = resources
        self.heading_counts: dict[str, int] = {}
        self.summary = ""
        self.title = ""
        self.toc: list[tuple[int, str, str]] = []

    def render(self, markdown: str) -> str:
        return self.render_blocks(markdown.splitlines())

    def render_blocks(self, lines: list[str]) -> str:
        parts: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue

            if stripped.startswith("<!--"):
                while i < len(lines) and "-->" not in lines[i]:
                    i += 1
                i += 1
                continue

            heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading:
                level = len(heading.group(1))
                text = heading.group(2).strip()
                anchor = self.unique_heading_id(strip_markdown(text))
                label = self.render_inline(text)
                plain_text = strip_markdown(text)
                if not self.title:
                    self.title = plain_text
                elif level <= 3:
                    self.toc.append((level, anchor, plain_text))
                parts.append(
                    f'<h{level} id="{anchor}">'
                    f'<a class="heading-anchor" href="#{anchor}" aria-label="Link to this section">#</a>'
                    f"{label}</h{level}>"
                )
                i += 1
                continue

            if stripped.startswith("```"):
                lang = normalize_lang(stripped[3:])
                i += 1
                code_lines: list[str] = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1
                class_attr = f' class="language-{lang}"' if lang else ""
                code = html.escape("\n".join(code_lines))
                parts.append(
                    '<div class="code-block"><pre>'
                    f"<code{class_attr}>{code}</code>"
                    "</pre></div>"
                )
                continue

            if self.is_table(lines, i):
                table_html, i = self.render_table(lines, i)
                parts.append(table_html)
                continue

            if self.is_list_item(line):
                list_html, i = self.render_list(lines, i)
                parts.append(list_html)
                continue

            para_lines = [stripped]
            i += 1
            while i < len(lines):
                candidate = lines[i]
                if not candidate.strip():
                    break
                if candidate.strip().startswith("<!--"):
                    break
                if re.match(r"^(#{1,6})\s+", candidate.strip()):
                    break
                if candidate.strip().startswith("```"):
                    break
                if self.is_table(lines, i):
                    break
                if self.is_list_item(candidate):
                    break
                para_lines.append(candidate.strip())
                i += 1
            paragraph = " ".join(para_lines)
            if not self.summary:
                self.summary = strip_markdown(paragraph)
            parts.append(f"<p>{self.render_inline(paragraph)}</p>")
        return "\n".join(parts)

    def unique_heading_id(self, text: str) -> str:
        base = slugify(text)
        count = self.heading_counts.get(base, 0) + 1
        self.heading_counts[base] = count
        if count == 1:
            return base
        return f"{base}-{count}"

    def is_list_item(self, line: str) -> re.Match[str] | None:
        return re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)

    def render_list(self, lines: list[str], start: int) -> tuple[str, int]:
        first = self.is_list_item(lines[start])
        assert first is not None
        base_indent = len(first.group(1))
        ordered = first.group(2).endswith(".")
        tag = "ol" if ordered else "ul"
        items: list[str] = [f"<{tag}>"]
        i = start

        while i < len(lines):
            while i < len(lines) and not lines[i].strip():
                i += 1
            match = self.is_list_item(lines[i]) if i < len(lines) else None
            if match is None:
                break
            indent = len(match.group(1))
            same_kind = match.group(2).endswith(".") == ordered
            if indent != base_indent or not same_kind:
                break

            item_lines = [match.group(3)]
            i += 1
            saw_blank = False
            while i < len(lines):
                if not lines[i].strip():
                    item_lines.append("")
                    saw_blank = True
                    i += 1
                    continue
                nested = self.is_list_item(lines[i])
                if nested is not None and len(nested.group(1)) <= base_indent:
                    break
                current_indent = len(lines[i]) - len(lines[i].lstrip(" "))
                if current_indent <= base_indent and (saw_blank or nested is None):
                    break
                if len(lines[i]) > base_indent + 2:
                    item_lines.append(lines[i][base_indent + 2 :])
                else:
                    item_lines.append(lines[i].lstrip())
                saw_blank = False
                i += 1

            item_html = self.render_blocks(item_lines)
            items.append(f"<li>{item_html}</li>")

        items.append(f"</{tag}>")
        return "\n".join(items), i

    def is_table(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        if "|" not in lines[index]:
            return False
        separator = lines[index + 1].strip()
        return bool(re.match(r"^\|?[\s:-]+\|[\s|:-]*$", separator))

    def split_table_row(self, row: str) -> list[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [cell.strip() for cell in row.split("|")]

    def render_table(self, lines: list[str], start: int) -> tuple[str, int]:
        rows = [self.split_table_row(lines[start])]
        i = start + 2
        while i < len(lines) and lines[i].strip().startswith("|"):
            rows.append(self.split_table_row(lines[i]))
            i += 1

        header = rows[0]
        body = rows[1:]
        parts = ['<div class="table-wrap"><table><thead><tr>']
        for cell in header:
            parts.append(f"<th>{self.render_inline(cell)}</th>")
        parts.append("</tr></thead><tbody>")
        for row in body:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{self.render_inline(cell)}</td>")
            parts.append("</tr>")
        parts.append("</tbody></table></div>")
        return "".join(parts), i

    def render_inline(self, text: str) -> str:
        rendered: list[str] = []
        cursor = 0
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
            rendered.append(self.render_inline_no_links(text[cursor : match.start()]))
            label = self.render_inline_no_links(match.group(1))
            target = match.group(2)
            href = self.link_href(target)
            external = is_external_link(target)
            attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
            rendered.append(f'<a href="{html.escape(href)}"{attrs}>{label}</a>')
            cursor = match.end()
        rendered.append(self.render_inline_no_links(text[cursor:]))
        return "".join(rendered)

    def render_inline_no_links(self, text: str) -> str:
        parts = re.split(r"(`[^`]+`)", text)
        rendered: list[str] = []
        for part in parts:
            if part.startswith("`") and part.endswith("`"):
                rendered.append(f"<code>{html.escape(part[1:-1])}</code>")
            else:
                rendered.append(self.render_inline_text(part))
        return "".join(rendered)

    def render_inline_text(self, text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
        text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"<em>\1</em>", text)
        return text

    def link_href(self, target: str) -> str:
        if is_external_link(target) or target.startswith("#"):
            return target

        resolved, frag = resolve_local_target(self.page.source, target)
        if resolved is None:
            return target

        suffix = f"#{frag}" if frag else ""
        if resolved == self.page.source and not target.startswith("#"):
            return suffix or "./"

        if resolved in self.pages:
            return relative_href(
                self.page.output_file.parent,
                self.pages[resolved].output_file,
                trailing_slash=True,
            ) + suffix

        if resolved in self.resources:
            return relative_href(
                self.page.output_file.parent,
                output_resource_path(resolved),
            ) + suffix

        if resolved.exists():
            rel = repo_rel(resolved)
            if resolved.is_dir():
                return f"{REPO_URL}/tree/main/{rel}{suffix}"
            return f"{REPO_URL}/blob/main/{rel}{suffix}"

        return target


def github_blob_url(source: Path) -> str:
    return f"{REPO_URL}/blob/main/{repo_rel(source)}"


def page_excerpt(page: Page) -> str:
    if not page.summary:
        return "Telepact documentation rendered from the repository source."
    summary = re.sub(r"\s+", " ", page.summary)
    return summary[:155].rstrip() + ("..." if len(summary) > 155 else "")


def page_by_rel_source(pages: dict[Path, Page], rel_source: str) -> Page | None:
    for page in pages.values():
        if page.rel_source == rel_source:
            return page
    return None


def nav_groups(pages: dict[Path, Page]) -> list[NavGroup]:
    doc_root = GENERATED_DOCS_SOURCE_DIR
    example_root = doc_root / "examples"
    groups: list[NavGroup] = []

    root_items: list[NavLink] = []
    home_page = page_for_source(pages, doc_root / "index.md")
    if home_page is not None:
        root_items.append(NavLink(home_page.title, home_page.rel_source))

    root_files = [
        child for child in doc_root.iterdir()
        if child.is_file()
        and child.suffix == ".md"
        and child.name not in {"README.md", "index.md"}
    ]
    for child in sort_nav_paths(root_files):
        page = page_for_source(pages, child)
        if page is None:
            continue
        root_items.append(NavLink(page.title, page.rel_source))
    if root_items:
        groups.append(NavGroup(heading="Start Here", items=root_items))

    top_level_dirs = [
        child for child in doc_root.iterdir()
        if child.is_dir() and child != example_root
    ]
    for directory in sort_nav_paths(top_level_dirs, order_overrides=TOP_LEVEL_DOC_DIR_ORDER):
        landing = directory_landing_page(pages, directory)
        heading = landing.title if landing is not None else display_name(directory)
        items = nav_links_for_directory(pages, directory)
        subgroups: list[NavSubgroup] = []
        child_dirs = [child for child in directory.iterdir() if child.is_dir()]
        for child_dir in sort_nav_paths(child_dirs):
            links = nav_links_for_directory(pages, child_dir)
            if not links:
                continue
            subgroups.append(
                NavSubgroup(
                    heading=display_name(child_dir),
                    items=links,
                )
            )
        groups.append(NavGroup(heading=heading, items=items, subgroups=subgroups))
    return groups


def render_nav_link(current: Page, pages: dict[Path, Page], resources: set[Path], item: NavLink) -> str:
    target_path = (
        GENERATED_DOCS_SOURCE_DIR / item.target
        if not item.target.startswith(ALLOWED_PREFIXES)
        else REPO_ROOT / item.target
    )
    active = ""
    href = item.target
    if target_path.suffix == ".md":
        page = page_by_rel_source(pages, item.target)
        if page is not None:
            active = ' class="active"' if page.source == current.source else ""
            href = relative_href(current.output_file.parent, page.output_file, trailing_slash=True)
        else:
            href = f"{REPO_URL}/blob/main/{item.target}"
    else:
        if target_path in resources:
            href = relative_href(current.output_file.parent, output_resource_path(target_path))
        elif target_path.exists():
            href = f"{REPO_URL}/blob/main/{item.target}"
    return f'<li><a{active} href="{html.escape(href)}">{html.escape(item.label)}</a></li>'


def render_nav(current: Page, pages: dict[Path, Page], resources: set[Path]) -> str:
    groups: list[str] = []
    for group in nav_groups(pages):
        parts: list[str] = []
        if group.items:
            links = [
                render_nav_link(current, pages, resources, item)
                for item in group.items
            ]
            parts.append(f"<ul>{''.join(links)}</ul>")
        for subgroup in group.subgroups:
            links = [
                render_nav_link(current, pages, resources, item)
                for item in subgroup.items
            ]
            parts.append(
                '<div class="docs-nav-subgroup">'
                f'<div class="docs-nav-subheading">{html.escape(subgroup.heading)}</div>'
                f"<ul>{''.join(links)}</ul>"
                "</div>"
            )
        groups.append(
            '<section class="docs-nav-group">'
            f"<h3>{html.escape(group.heading)}</h3>"
            f"{''.join(parts)}"
            "</section>"
        )
    return "".join(groups)


def render_toc(current: Page) -> str:
    if not current.toc:
        return ""
    items = []
    for level, anchor, title in current.toc:
        class_name = f"toc-level-{level}"
        items.append(
            f'<li class="{class_name}"><a href="#{anchor}">{html.escape(title)}</a></li>'
        )
    return (
        '<aside class="docs-toc">'
        '<div class="sidebar-card">'
        '<div class="sidebar-label">On this page</div>'
        f"<ul>{''.join(items)}</ul>"
        "</div>"
        "</aside>"
    )


def page_shell(page: Page, body_html: str, pages: dict[Path, Page], resources: set[Path]) -> str:
    css_href = relative_href(page.output_file.parent, DOCS_DIR / "assets" / "docs.css")
    docs_search_script_href = relative_href(page.output_file.parent, DOCS_DIR / "assets" / "docs-search.js")
    docs_search_index_href = relative_href(page.output_file.parent, DOCS_DIR / "assets" / "search-index.json")
    home_href = relative_href(page.output_file.parent, SITE_DIR / "index.html")
    docs_home_href = relative_href(page.output_file.parent, DOCS_DIR / "index.html", trailing_slash=True)
    favicon_href = relative_href(page.output_file.parent, SITE_DIR / "favicon.ico")
    canonical = posixpath.join(BASE_URL.rstrip("/"), page.url.lstrip("/"))
    prism_scripts = "\n".join(f'<script src="{src}"></script>' for src in PRISM_JS)
    return render_template(
        DOCS_TEMPLATE,
        {
            "PAGE_TITLE": html.escape(page.title),
            "PAGE_DESCRIPTION": html.escape(page_excerpt(page)),
            "CANONICAL_URL": html.escape(canonical),
            "FAVICON_HREF": html.escape(favicon_href),
            "PRISM_CSS_HREF": html.escape(PRISM_CSS),
            "DOCS_CSS_HREF": html.escape(css_href),
            "DOCS_SEARCH_SCRIPT_HREF": html.escape(docs_search_script_href),
            "DOCS_SEARCH_INDEX_HREF": html.escape(docs_search_index_href),
            "HOME_HREF": html.escape(home_href),
            "DOCS_HOME_HREF": html.escape(docs_home_href),
            "REPO_URL": html.escape(REPO_URL),
            "NAVIGATION": render_nav(page, pages, resources),
            "BODY_HTML": body_html,
            "TOC": render_toc(page),
            "PRISM_SCRIPTS": prism_scripts,
        },
    )


def write_css() -> None:
    assets_dir = DOCS_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DOCS_CSS_SOURCE, assets_dir / "docs.css")
    shutil.copy2(DOCS_SEARCH_SCRIPT_SOURCE, assets_dir / "docs-search.js")


def write_search_index(pages: dict[Path, Page]) -> None:
    search_index_path = DOCS_DIR / "assets" / "search-index.json"
    search_index_path.parent.mkdir(parents=True, exist_ok=True)
    search_pages = [
        SearchablePage(
            title=page.title,
            path=relative_href(DOCS_DIR, page.output_file, trailing_slash=True),
            markdown=page.source.read_text(encoding="utf-8"),
        )
        for page in sorted(pages.values(), key=lambda current: current.url)
    ]
    search_index = build_search_index(search_pages)
    search_index_path.write_text(
        json.dumps(search_index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_pages(pages: dict[Path, Page], resources: set[Path]) -> None:
    for page in pages.values():
        renderer = MarkdownRenderer(page, pages, resources)
        markdown = page.source.read_text(encoding="utf-8")
        renderer.render(markdown)
        page.title = renderer.title or page.source.stem
        page.summary = renderer.summary
        page.toc = renderer.toc
    write_search_index(pages)

    for page in pages.values():
        renderer = MarkdownRenderer(page, pages, resources)
        markdown = page.source.read_text(encoding="utf-8")
        body_html = renderer.render(markdown)
        page.output_file.parent.mkdir(parents=True, exist_ok=True)
        page.output_file.write_text(page_shell(page, body_html, pages, resources), encoding="utf-8")

    for resource in resources:
        target = output_resource_path(resource)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(resource, target)


def copy_markdown_docs() -> None:
    for source in sorted((REPO_ROOT / "doc").rglob("*.md")):
        target = output_markdown_doc_path(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def write_llms(pages: dict[Path, Page]) -> None:
    markdown_directory_url = site_url("markdown-docs/")
    lines = [
        "# Telepact",
        "",
        "> Telepact is a thin but powerful RPC framework built on JSON.",
        "",
        "This site publishes the original documentation markdown files for AI agents.",
        "",
        f"- [HTML documentation]({site_url('docs/')})",
        f"- [Markdown documentation directory]({markdown_directory_url})",
        f"- [Markdown docs entrypoint]({site_url('markdown-docs/index.md')})",
        "",
        "## Original documentation markdown",
        "",
    ]

    for source in sorted((REPO_ROOT / "doc").rglob("*.md")):
        rel_path = source.relative_to(REPO_ROOT / "doc").as_posix()
        page = pages.get(source)
        title = page.title if page is not None and page.title else display_name(source)
        lines.append(f"- [{title}]({site_url(f'markdown-docs/{rel_path}')})")

    LLMS_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sitemap(pages: dict[Path, Page]) -> None:
    urls: dict[str, str] = {
        "": datetime.now(timezone.utc).date().isoformat(),
    }
    for page in sorted(pages.values(), key=lambda value: value.url):
        lastmod = datetime.fromtimestamp(page.source.stat().st_mtime, timezone.utc).date().isoformat()
        urls[page.url] = lastmod

    parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lastmod in urls.items():
        full_url = posixpath.join(BASE_URL.rstrip("/"), url.lstrip("/"))
        parts.extend([
            "  <url>",
            f"    <loc>{full_url}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            "    <changefreq>weekly</changefreq>",
            "    <priority>0.8</priority>" if url else "    <priority>1.0</priority>",
            "  </url>",
        ])
    parts.append("</urlset>")
    (SITE_DIR / "sitemap.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    write_generated_docs()
    copy_static_files()
    snippet_count = write_home_page()
    pages, resources = discover_pages()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    MARKDOWN_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    write_css()
    write_pages(pages, resources)
    copy_markdown_docs()
    write_cname()
    write_robots()
    write_llms(pages)
    write_sitemap(pages)
    if GENERATED_SOURCE_DIR.exists():
        shutil.rmtree(GENERATED_SOURCE_DIR)
    print(
        f"Generated home page from {snippet_count} snippets, "
        f"{len(pages)} documentation pages, and {len(resources)} copied resources into {SITE_DIR}"
    )


if __name__ == "__main__":
    main()
