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

import click
import posixpath
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

SKILL_FRONTMATTER = """---
name: telepact-api
description: Read, draft, and implement Telepact APIs.
license: Apache-2.0
---"""

RAW_GITHUB_PATTERN = re.compile(
    r"^https://raw\.githubusercontent\.com/Telepact/telepact/refs/heads/main/([^\?#]+)(.*)$"
)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FIRST_HEADING_PATTERN = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)
INLINED_DOC_SOURCE_PATHS = (
    "doc/schema-guide.md",
    "doc/faq.md",
    "doc/versions.md",
)


def _read_file(file_path: Path) -> str:
    with file_path.open("r", encoding="utf-8") as file:
        return file.read()


def _write_file(file_path: Path, content: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        file.write(content)


def _split_link_suffix(link_target: str) -> Tuple[str, str]:
    if "#" in link_target:
        path_part, anchor = link_target.split("#", 1)
        return path_part, f"#{anchor}"
    return link_target, ""


def _to_repo_relative(source_path: str, link_target: str) -> str:
    source_dir = posixpath.dirname(source_path)
    return posixpath.normpath(posixpath.join(source_dir, link_target))


def _to_relative_target(destination_path: str, mapped_target_path: str) -> str:
    destination_dir = posixpath.dirname(destination_path)
    relative_target = posixpath.relpath(mapped_target_path, destination_dir or ".")
    if relative_target == ".":
        return relative_target
    if not relative_target.startswith("."):
        relative_target = f"./{relative_target}"
    return relative_target


def _slugify(text: str) -> str:
    slug = text.lower()
    slug = slug.replace(".", "-")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _rewrite_links(
    content: str,
    source_path: str,
    destination_path: str,
    source_to_destination_map: Dict[str, str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        link_text = match.group(1)
        link_target = match.group(2)

        path_part, suffix = _split_link_suffix(link_target)

        if not path_part:
            return match.group(0)

        raw_match = RAW_GITHUB_PATTERN.match(path_part)
        if raw_match:
            raw_repo_path = posixpath.normpath(raw_match.group(1))
            if raw_repo_path in source_to_destination_map:
                rewritten = _to_relative_target(destination_path, source_to_destination_map[raw_repo_path])
                return f"[{link_text}]({rewritten}{suffix})"
            return match.group(0)

        if "://" in path_part or path_part.startswith("#"):
            return match.group(0)

        repo_relative_target = _to_repo_relative(source_path, path_part)
        if repo_relative_target in source_to_destination_map:
            rewritten = _to_relative_target(destination_path, source_to_destination_map[repo_relative_target])
            return f"[{link_text}]({rewritten}{suffix})"

        return match.group(0)

    return MARKDOWN_LINK_PATTERN.sub(replace, content)


def _extract_first_heading_anchor(content: str, fallback: str) -> str:
    heading_match = FIRST_HEADING_PATTERN.search(content)
    if heading_match:
        anchor = _slugify(heading_match.group(1))
        if anchor:
            return anchor
    return fallback


def _rewrite_inlined_doc_links(
    content: str,
    source_path: str,
    destination_path: str,
    inlined_doc_anchor_map: Dict[str, str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        link_text = match.group(1)
        link_target = match.group(2)

        path_part, suffix = _split_link_suffix(link_target)
        if not path_part:
            return match.group(0)

        raw_match = RAW_GITHUB_PATTERN.match(path_part)
        if raw_match:
            repo_relative_target = posixpath.normpath(raw_match.group(1))
        elif "://" in path_part or path_part.startswith("#"):
            return match.group(0)
        else:
            repo_relative_target = _to_repo_relative(source_path, path_part)

        doc_anchor = inlined_doc_anchor_map.get(repo_relative_target)
        if not doc_anchor:
            return match.group(0)

        anchor_or_suffix = suffix if suffix else f"#{doc_anchor}"
        if destination_path == "SKILL.md":
            return f"[{link_text}]({anchor_or_suffix})"

        skill_relative_target = _to_relative_target(destination_path, "SKILL.md")
        return f"[{link_text}]({skill_relative_target}{anchor_or_suffix})"

    return MARKDOWN_LINK_PATTERN.sub(replace, content)


def _collect_common_json_files(repo_root: Path) -> List[Tuple[str, str, str]]:
    common_files: List[Tuple[str, str, str]] = []
    for common_file_path in sorted((repo_root / "common").glob("*.json")):
        if common_file_path.name == "json-schema.json":
            continue
        repo_relative_path = f"common/{common_file_path.name}"
        anchor = _slugify(common_file_path.name)
        common_files.append((repo_relative_path, anchor, _read_file(common_file_path).rstrip("\n")))
    return common_files


def _rewrite_common_json_links_to_anchors(
    content: str, source_path: str, common_json_anchor_map: Dict[str, str]
) -> str:
    def replace(match: re.Match[str]) -> str:
        link_text = match.group(1)
        link_target = match.group(2)

        path_part, _ = _split_link_suffix(link_target)
        if not path_part:
            return match.group(0)

        raw_match = RAW_GITHUB_PATTERN.match(path_part)
        if raw_match:
            repo_relative_target = posixpath.normpath(raw_match.group(1))
        elif "://" in path_part or path_part.startswith("#"):
            return match.group(0)
        else:
            repo_relative_target = _to_repo_relative(source_path, path_part)

        anchor = common_json_anchor_map.get(repo_relative_target)
        if anchor:
            return f"[{link_text}](#{anchor})"

        return match.group(0)

    return MARKDOWN_LINK_PATTERN.sub(replace, content)


def _append_common_json_appendix(content: str, source_path: str, repo_root: Path) -> str:
    common_json_files = _collect_common_json_files(repo_root)
    if not common_json_files:
        return content

    common_json_anchor_map = {repo_path: anchor for repo_path, anchor, _ in common_json_files}
    rewritten_content = _rewrite_common_json_links_to_anchors(
        content, source_path, common_json_anchor_map
    )

    appendix = "\n\n## Appendix\n\n"
    for _, anchor, json_content in common_json_files:
        appendix += f"### {anchor}\n\n"
        appendix += f"```json\n{json_content}\n```\n\n"

    return rewritten_content.rstrip() + appendix


def _build_source_to_destination_map() -> Dict[str, str]:
    source_to_destination_map: Dict[str, str] = {
        "doc/motivation.md": "references/motivation.md",
        "doc/example.md": "references/example.md",
        "lib/ts/README.md": "references/ts.md",
        "lib/py/README.md": "references/py.md",
        "lib/java/README.md": "references/java.md",
        "lib/go/README.md": "references/go.md",
        "sdk/cli/README.md": "references/cli.md",
        "sdk/console/README.md": "references/console.md",
        "sdk/prettier/README.md": "references/prettier.md",
        "LICENSE": "references/LICENSE",
        "NOTICE": "references/NOTICE",
        "common/json-schema.json": "references/json-schema.json",
    }
    return source_to_destination_map


def _render_skill(readme_path: Path, output_dir: Path) -> None:
    repo_root = readme_path.parent
    source_to_destination_map = _build_source_to_destination_map()
    inlined_docs: List[Tuple[str, str]] = []
    inlined_doc_anchor_map: Dict[str, str] = {}

    for inlined_doc_source_path in INLINED_DOC_SOURCE_PATHS:
        inlined_doc_file_path = repo_root / inlined_doc_source_path
        if not inlined_doc_file_path.exists():
            raise click.ClickException(f"Source file not found: {inlined_doc_source_path}")

        inlined_doc_content = _read_file(inlined_doc_file_path)
        inlined_docs.append((inlined_doc_source_path, inlined_doc_content))
        inlined_doc_anchor_map[inlined_doc_source_path] = _extract_first_heading_anchor(
            inlined_doc_content, _slugify(posixpath.basename(inlined_doc_source_path))
        )

    references_dir = output_dir / "references"
    if references_dir.exists():
        shutil.rmtree(references_dir)
    references_dir.mkdir(parents=True, exist_ok=True)

    readme_content = _read_file(readme_path)
    rewritten_readme = _rewrite_links(
        readme_content,
        source_path="README.md",
        destination_path="SKILL.md",
        source_to_destination_map=source_to_destination_map,
    )
    rewritten_readme = _rewrite_inlined_doc_links(
        rewritten_readme,
        source_path="README.md",
        destination_path="SKILL.md",
        inlined_doc_anchor_map=inlined_doc_anchor_map,
    )
    skill_content = f"{SKILL_FRONTMATTER}\n\n{rewritten_readme.rstrip()}"

    for inlined_doc_source_path, inlined_doc_content in inlined_docs:
        rewritten_inlined_doc = _rewrite_links(
            inlined_doc_content,
            source_path=inlined_doc_source_path,
            destination_path="SKILL.md",
            source_to_destination_map=source_to_destination_map,
        )
        rewritten_inlined_doc = _rewrite_inlined_doc_links(
            rewritten_inlined_doc,
            source_path=inlined_doc_source_path,
            destination_path="SKILL.md",
            inlined_doc_anchor_map=inlined_doc_anchor_map,
        )
        if inlined_doc_source_path == "doc/schema-guide.md":
            rewritten_inlined_doc = _append_common_json_appendix(
                rewritten_inlined_doc, inlined_doc_source_path, repo_root
            )

        skill_content += f"\n\n{rewritten_inlined_doc.rstrip()}"

    _write_file(output_dir / "SKILL.md", skill_content)

    for source_path, destination_path in source_to_destination_map.items():
        source_file_path = repo_root / source_path
        if not source_file_path.exists():
            raise click.ClickException(f"Source file not found: {source_path}")

        source_content = _read_file(source_file_path)
        if source_file_path.suffix.lower() == ".md":
            source_content = _rewrite_links(
                source_content,
                source_path=source_path,
                destination_path=destination_path,
                source_to_destination_map=source_to_destination_map,
            )
            source_content = _rewrite_inlined_doc_links(
                source_content,
                source_path=source_path,
                destination_path=destination_path,
                inlined_doc_anchor_map=inlined_doc_anchor_map,
            )

        _write_file(output_dir / destination_path, source_content)


@click.command()
@click.argument("readme_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_dir", type=click.Path(path_type=Path))
def skill(readme_path: Path, output_dir: Path) -> None:
    """
    Generate a skill folder from README plus referenced project docs.
    """
    _render_skill(readme_path, output_dir)
    click.echo(f"Skill generated at: {output_dir}")
