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
from pathlib import Path
from typing import Iterable

import click
from lxml import etree as ET
import toml

_BUMP_VERSION_RE = re.compile(r"^Bump version to (\S+)")
_RELEASE_TARGETS_HEADER = "Release targets:"
_PYPI_PRERELEASE_RE = re.compile(r"^(\d+\.\d+\.\d+)-(alpha|beta|rc)\.(\d+)$")


def _find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "VERSION.txt").exists():
            return candidate
    raise click.ClickException("Unable to locate repo root (VERSION.txt not found).")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {path}")


def _read_json(path: Path) -> dict:
    try:
        return json.loads(_read_text(path))
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in {path}: {e}")


def _read_package_json_name(path: Path) -> str:
    data = _read_json(path)
    name = data.get("name")
    if not isinstance(name, str) or not name:
        raise click.ClickException(f"Missing/invalid package name in {path}")
    return name


def _read_poetry_name(pyproject_path: Path) -> str:
    try:
        data = toml.loads(_read_text(pyproject_path))
    except toml.TomlDecodeError as e:
        raise click.ClickException(f"Invalid TOML in {pyproject_path}: {e}")
    poetry = data.get("tool", {}).get("poetry", {})
    name = poetry.get("name")
    if not isinstance(name, str) or not name:
        raise click.ClickException(f"Missing/invalid [tool.poetry].name in {pyproject_path}")
    return name


def _read_go_module_path(go_mod_path: Path) -> str:
    for line in _read_text(go_mod_path).splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        if line.startswith("module "):
            parts = line.split()
            if len(parts) >= 2 and parts[1]:
                return parts[1]
    raise click.ClickException(f"Unable to find module path in {go_mod_path}")


def _read_maven_gav(pom_path: Path) -> tuple[str, str]:
    parser = ET.XMLParser(remove_blank_text=True)
    try:
        tree = ET.parse(str(pom_path), parser)
    except OSError as e:
        raise click.ClickException(f"Unable to read {pom_path}: {e}")

    root = tree.getroot()
    namespace_uri = root.nsmap.get(None)
    ns = {"m": namespace_uri} if namespace_uri else {}

    def find_text(xpath: str) -> str | None:
        value = root.findtext(xpath, namespaces=ns) if ns else root.findtext(xpath)
        if value is None:
            return None
        value = value.strip()
        return value if value else None

    group_id = find_text("m:groupId") or find_text("m:parent/m:groupId")
    artifact_id = find_text("m:artifactId")
    version = find_text("m:version") or find_text("m:parent/m:version")

    if not group_id or not artifact_id:
        raise click.ClickException(f"Missing/invalid Maven coordinates in {pom_path}")
    if not version:
        raise click.ClickException(f"Missing/invalid Maven version in {pom_path}")

    return f"{group_id}:{artifact_id}", version


def _iter_git_commits(repo_root: Path) -> list[tuple[str, str, str]]:
    try:
        out = subprocess.run(
            ["git", "log", "--format=%H%x1f%s%x1f%b%x1e"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"git log failed: {e}")

    commits: list[tuple[str, str, str]] = []
    for record in out.split("\x1e"):
        record = record.strip("\n")
        if not record.strip():
            continue
        fields = record.split("\x1f")
        if len(fields) < 3:
            continue
        sha = fields[0].strip()
        subject = fields[1].strip()
        body = fields[2]
        commits.append((sha, subject, body))
    return commits


def _extract_release_targets(commit_body: str) -> list[str]:
    lines = [line.strip() for line in commit_body.splitlines()]
    try:
        header_index = lines.index(_RELEASE_TARGETS_HEADER)
    except ValueError:
        return []
    targets: list[str] = []
    for line in lines[header_index + 1 :]:
        if not line:
            break
        targets.append(line)
    return targets


def _latest_released_versions(
    repo_root: Path,
    targets: list[str],
    pending_version: str | None = None,
    pending_targets: Iterable[str] = (),
) -> dict[str, str]:
    found: dict[str, str] = {}
    needed = set(targets)

    if pending_version:
        for target in pending_targets:
            if target in needed:
                found[target] = pending_version

    for _, subject, body in _iter_git_commits(repo_root):
        match = _BUMP_VERSION_RE.match(subject)
        if not match:
            continue
        version = match.group(1)
        release_targets = _extract_release_targets(body)
        if not release_targets:
            continue
        for target in release_targets:
            if target in needed and target not in found:
                found[target] = version
        if len(found) == len(needed):
            break

    return found


def _to_pypi_version(version: str) -> str:
    match = _PYPI_PRERELEASE_RE.match(version)
    if not match:
        return version

    base, stage, number = match.groups()
    suffix_by_stage = {"alpha": "a", "beta": "b", "rc": "rc"}
    return f"{base}{suffix_by_stage[stage]}{number}"


def write_doc_versions(
    repo_root: Path,
    output: Path | None,
    pending_version: str | None = None,
    pending_targets: Iterable[str] = (),
) -> Path:
    repo_root = _find_repo_root(repo_root)

    version_by_target = _latest_released_versions(
        repo_root,
        targets=["go", "java", "py", "ts", "cli", "console", "prettier"],
        pending_version=pending_version,
        pending_targets=pending_targets,
    )

    go_module = _read_go_module_path(repo_root / "lib/go/go.mod")
    java_package, _ = _read_maven_gav(repo_root / "lib/java/pom.xml")
    py_package = _read_poetry_name(repo_root / "lib/py/pyproject.toml")
    ts_package = _read_package_json_name(repo_root / "lib/ts/package.json")

    cli_package = _read_poetry_name(repo_root / "sdk/cli/pyproject.toml")
    console_package = _read_package_json_name(repo_root / "sdk/console/package.json")
    prettier_package = _read_package_json_name(repo_root / "sdk/prettier/package.json")

    def fmt_version(target: str) -> str:
        version = version_by_target.get(target)
        if not version:
            return "—"
        if target == "go" and not version.startswith("v"):
            return f"v{version}"
        if target in {"py", "cli"}:
            return _to_pypi_version(version)
        return version

    rows: list[tuple[str, str, str, str]] = [
        ("Library (Go)", go_module, "Go module (proxy.golang.org)", fmt_version("go")),
        ("Library (Java)", java_package, "Maven Central", fmt_version("java")),
        ("Library (Python)", py_package, "PyPI", fmt_version("py")),
        ("Library (TypeScript)", ts_package, "npm", fmt_version("ts")),
        ("SDK (CLI)", cli_package, "PyPI", fmt_version("cli")),
        ("SDK (Console)", console_package, "npm", fmt_version("console")),
        ("SDK (Prettier)", prettier_package, "npm", fmt_version("prettier")),
    ]

    out_lines = [
        "# Versions",
        "",
        "<!-- This file is auto-generated by `telepact_project_cli doc-versions`. Do not edit by hand. -->",
        "",
        "This table tracks the latest **published** Telepact distributions by registry.",
        "Repository source versions may be ahead of these values between releases.",
        "",
        "| Kind | Package | Registry | Version |",
        "|---|---|---|---|",
    ]
    for kind, package, published, row_version in rows:
        out_lines.append(f"| {kind} | `{package}` | {published} | `{row_version}` |")
    out_lines.append("")

    out_path = (output.resolve() if output is not None else (repo_root / "doc" / "versions.md"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    return out_path


@click.command()
@click.option(
    "--repo-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Path within the repo; the actual root is auto-detected by VERSION.txt.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Where to write the markdown file (default: doc/versions.md at repo root).",
)
def doc_versions(repo_root: Path, output: Path | None) -> None:
    write_doc_versions(repo_root, output)
