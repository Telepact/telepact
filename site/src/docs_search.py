from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
TABLE_SEPARATOR_RE = re.compile(r"^\|?[\s:-]+\|[\s|:-]*$")


@dataclass(frozen=True)
class SearchablePage:
    title: str
    path: str
    markdown: str


def build_search_index(pages: Iterable[SearchablePage]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for page in pages:
        entries.extend(extract_page_entries(page))
    return entries


def extract_page_entries(page: SearchablePage) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    heading_counts: dict[str, int] = {}
    current_heading = page.title
    current_anchor = ""
    current_block: list[str] = []
    in_code_block = False
    in_comment = False

    def flush() -> None:
        nonlocal current_block
        content = normalize_plain_text(" ".join(current_block))
        current_block = []
        if not content:
            return
        heading = "" if current_heading == page.title else current_heading
        search_text = normalize_search_text(" ".join(part for part in (page.title, heading, content) if part))
        target = page.path
        if current_anchor:
            target += f"#{current_anchor}"
        entries.append({
            "title": page.title,
            "section": heading,
            "path": target,
            "content": content,
            "searchText": search_text,
        })

    for raw_line in page.markdown.splitlines():
        stripped = raw_line.strip()

        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            flush()
            current_heading = strip_markdown(heading_match.group(2).strip()) or page.title
            current_anchor = unique_heading_id(current_heading, heading_counts)
            continue

        if not stripped:
            flush()
            continue

        if TABLE_SEPARATOR_RE.match(stripped):
            continue

        line = stripped
        line = LIST_ITEM_RE.sub("", line)
        line = re.sub(r"^>\s*", "", line)
        line = line.replace("|", " ")
        current_block.append(line)

    flush()
    return entries


def unique_heading_id(text: str, heading_counts: dict[str, int]) -> str:
    base = slugify(text)
    count = heading_counts.get(base, 0) + 1
    heading_counts[base] = count
    if count == 1:
        return base
    return f"{base}-{count}"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "section"


def strip_markdown(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    return value.strip()


def normalize_plain_text(value: str) -> str:
    value = strip_markdown(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_search_text(value: str) -> str:
    value = normalize_plain_text(value).lower()
    return re.sub(r"\s+", " ", value)
