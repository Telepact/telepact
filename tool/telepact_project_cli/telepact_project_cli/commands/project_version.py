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

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import click
import toml
from github import Github, InputGitTreeElement
from lxml import etree as ET
from ruamel.yaml import YAML

from .doc_versions import write_doc_versions
from ..release_plan import compute_release_manifest, write_release_manifest

yaml = YAML()
PROJECT_FILES = [
    "lib/java/pom.xml",
    "lib/py/pyproject.toml",
    "lib/ts/package.json",
    "bind/dart/pubspec.yaml",
    "bind/dart/package.json",
    "sdk/cli/pyproject.toml",
    "sdk/prettier/package.json",
    "sdk/console/package.json",
]


@dataclass(frozen=True)
class BumpResult:
    new_version: str
    commit_message: str
    edited_files: tuple[str, ...]


def _write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2) + "\n")


def _load_pyproject() -> dict:
    with open("pyproject.toml", "r") as f:
        return toml.load(f)


def _project_version(data: dict) -> str:
    project = data.get("project", {})
    if "version" in project:
        return project["version"]
    return data["tool"]["poetry"]["version"]


def _set_project_version(data: dict, version: str) -> dict:
    project = data.get("project")
    if isinstance(project, dict) and "version" in project:
        project["version"] = version
        return data

    data["tool"]["poetry"]["version"] = version
    return data


def _get_version_from_project_file(project_file: str) -> str:
    if project_file.endswith("pom.xml"):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(project_file, parser)
        root = tree.getroot()
        return root.find("{http://maven.apache.org/POM/4.0.0}version").text
    if project_file.endswith("package.json"):
        with open(project_file, "r") as f:
            data = json.load(f)
        return data["version"]
    if project_file.endswith("pyproject.toml"):
        return _project_version(_load_pyproject())
    if project_file.endswith("pubspec.yaml"):
        with open(project_file, "r") as f:
            data = yaml.load(f)
        return data["version"]
    raise ValueError(f"Unsupported project file type: {project_file}")


def _set_version_in_project_file(project_file: str, version: str) -> None:
    if project_file.endswith("pom.xml"):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(project_file, parser)
        root = tree.getroot()
        root.find("{http://maven.apache.org/POM/4.0.0}version").text = version
        tree.write(project_file, xml_declaration=True, encoding="utf-8", pretty_print=True)
        return
    if project_file.endswith("package.json"):
        with open(project_file, "r") as f:
            data = json.load(f)
        data["version"] = version
        _write_json(project_file, data)
        return
    if project_file.endswith("pyproject.toml"):
        with open(project_file, "r") as f:
            data = toml.load(f)
        data = _set_project_version(data, version)
        with open(project_file, "w") as f:
            toml.dump(data, f)
        return
    if project_file.endswith("pubspec.yaml"):
        with open(project_file, "r") as f:
            data = yaml.load(f)
        data["version"] = version
        with open(project_file, "w") as f:
            yaml.dump(data, f)
        return
    raise ValueError(f"Unsupported project file type: {project_file}")


def _update_and_get_lock_file_path(project_file: str) -> str | None:
    project_dir = os.path.dirname(project_file)
    if project_file.endswith("package.json") and os.path.exists(os.path.join(project_dir, "package-lock.json")):
        subprocess.run(["npm", "install"], cwd=project_dir, check=True)
        click.echo(f"Updated package-lock.json in {project_dir}")
        return os.path.join(project_dir, "package-lock.json")

    if project_file.endswith("pyproject.toml") and os.path.exists(os.path.join(project_dir, "uv.lock")):
        subprocess.run(["uv", "lock"], cwd=project_dir, check=True)
        click.echo(f"Updated uv.lock in {project_dir}")
        return os.path.join(project_dir, "uv.lock")

    if project_file.endswith("pubspec.yaml") and os.path.exists(os.path.join(project_dir, "pubspec.lock")):
        subprocess.run(["dart", "pub", "get"], cwd=project_dir, check=True)
        click.echo(f"Updated pubspec.lock in {project_dir}")
        return os.path.join(project_dir, "pubspec.lock")

    return None


def _bump_version(version: str) -> str:
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable not set.")
    return value


def _apply_version_bump(repo_root: Path, changed_paths: list[str], pr_number: int) -> BumpResult:
    version_file = repo_root / "VERSION.txt"
    if not version_file.exists():
        raise click.ClickException(f"Version file {version_file} does not exist.")

    version = version_file.read_text(encoding="utf-8").strip()
    new_version = _bump_version(version)
    version_file.write_text(new_version, encoding="utf-8")
    click.echo(f"Updated version file {version_file.relative_to(repo_root)} to version {new_version}")

    edited_files = [version_file.relative_to(repo_root).as_posix()]

    for project_file in PROJECT_FILES:
        project_path = repo_root / project_file
        if project_path.exists():
            _set_version_in_project_file(str(project_path), new_version)
            click.echo(f"Updated {project_file} to version {new_version}")
            edited_files.append(project_file)
        else:
            click.echo(f"Project file {project_file} does not exist.")

    for project_file in PROJECT_FILES:
        project_path = repo_root / project_file
        lock_file = _update_and_get_lock_file_path(str(project_path))
        if lock_file is not None:
            edited_files.append(Path(lock_file).relative_to(repo_root).as_posix())

    release_manifest = compute_release_manifest(
        repo_root,
        changed_paths=changed_paths,
        version=new_version,
        pr_number=pr_number,
    )
    manifest_path = write_release_manifest(repo_root, release_manifest)
    edited_files.append(manifest_path.relative_to(repo_root).as_posix())
    click.echo(f"Updated {manifest_path.relative_to(repo_root)}")

    doc_versions_path = write_doc_versions(
        repo_root,
        None,
        pending_version=new_version,
        pending_targets=list(release_manifest.targets),
    )
    edited_files.append(doc_versions_path.relative_to(repo_root).as_posix())
    click.echo(f"Updated {doc_versions_path.relative_to(repo_root)}")

    return BumpResult(
        new_version=new_version,
        commit_message=f"Bump version to {new_version} (#{pr_number})",
        edited_files=tuple(dict.fromkeys(edited_files)),
    )


def _commit_bump_via_git_data_api(repo, branch_ref: str, parent_sha: str, repo_root: Path, bump_result: BumpResult) -> str:
    parent_commit = repo.get_git_commit(parent_sha)
    tree_elements = [
        InputGitTreeElement(
            path=edited_file,
            mode="100644",
            type="blob",
            content=(repo_root / edited_file).read_text(encoding="utf-8"),
        )
        for edited_file in bump_result.edited_files
    ]
    new_tree = repo.create_git_tree(tree_elements, base_tree=parent_commit.tree)
    new_commit = repo.create_git_commit(
        message=bump_result.commit_message,
        tree=new_tree,
        parents=[parent_commit],
    )
    repo.get_git_ref(f"heads/{branch_ref}").edit(new_commit.sha)
    return new_commit.sha


def bump_pull_request_version(repo, pr, repo_root: Path | str = ".") -> tuple[str, str]:
    repo_root = Path(repo_root).resolve()
    changed_paths = sorted({file.filename for file in pr.get_files()})
    bump_result = _apply_version_bump(repo_root, changed_paths, pr.number)
    new_head_sha = _commit_bump_via_git_data_api(
        repo=repo,
        branch_ref=pr.head.ref,
        parent_sha=pr.head.sha,
        repo_root=repo_root,
        bump_result=bump_result,
    )
    click.echo(f"Created bump commit {new_head_sha} for version {bump_result.new_version}")
    return new_head_sha, bump_result.new_version


@click.command()
def get() -> None:
    for project_file in ["pom.xml", "package.json", "pyproject.toml", "pubspec.yaml"]:
        if os.path.exists(project_file):
            click.echo(_get_version_from_project_file(project_file), nl=False)
            return

    click.echo("No supported project file found.", nl=False)


@click.command()
@click.argument("version")
def set_version(version: str) -> None:
    updated = False

    for project_file in ["pom.xml", "package.json", "pyproject.toml", "pubspec.yaml"]:
        if os.path.exists(project_file):
            _set_version_in_project_file(project_file, version)
            click.echo(f"Set {project_file} to version {version}")
            updated = True

    if not updated:
        click.echo("No supported project file found.")


@click.command()
def bump() -> None:
    pr_number = int(_require_env("PR_NUMBER"))
    token = _require_env("GITHUB_TOKEN")
    repository = _require_env("GITHUB_REPOSITORY")

    g = Github(token)
    repo = g.get_repo(repository)
    pr = repo.get_pull(pr_number)
    bump_pull_request_version(repo, pr, Path("."))
