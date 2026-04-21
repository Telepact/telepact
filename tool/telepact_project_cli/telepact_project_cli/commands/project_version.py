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
from pathlib import Path

import click
import toml
from github import Github, InputGitTreeElement
from lxml import etree as ET
from ruamel.yaml import YAML

from .doc_versions import _read_existing_doc_versions, write_doc_versions
from ..github_utils import require_env, write_github_outputs
from ..release_plan import compute_release_manifest, find_repo_root, write_release_manifest

yaml = YAML()


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _load_pyproject(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return toml.load(file)


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


def _get_version_from_project_file(project_file: Path) -> str:
    if project_file.name == "pom.xml":
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(str(project_file), parser)
        root = tree.getroot()
        return root.find("{http://maven.apache.org/POM/4.0.0}version").text
    if project_file.name == "package.json":
        return json.loads(project_file.read_text(encoding="utf-8"))["version"]
    if project_file.name == "pyproject.toml":
        return _project_version(_load_pyproject(project_file))
    if project_file.name == "pubspec.yaml":
        return yaml.load(project_file.read_text(encoding="utf-8"))["version"]
    raise ValueError(f"Unsupported project file type: {project_file}")


def _set_version_in_project_file(project_file: Path, version: str) -> None:
    if project_file.name == "pom.xml":
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(str(project_file), parser)
        root = tree.getroot()
        root.find("{http://maven.apache.org/POM/4.0.0}version").text = version
        tree.write(str(project_file), xml_declaration=True, encoding="utf-8", pretty_print=True)
        return
    if project_file.name == "package.json":
        data = json.loads(project_file.read_text(encoding="utf-8"))
        data["version"] = version
        _write_json(project_file, data)
        return
    if project_file.name == "pyproject.toml":
        data = toml.loads(project_file.read_text(encoding="utf-8"))
        data = _set_project_version(data, version)
        with project_file.open("w", encoding="utf-8") as file:
            toml.dump(data, file)
        return
    if project_file.name == "pubspec.yaml":
        data = yaml.load(project_file.read_text(encoding="utf-8"))
        data["version"] = version
        with project_file.open("w", encoding="utf-8") as file:
            yaml.dump(data, file)
        return
    raise ValueError(f"Unsupported project file type: {project_file}")


def _update_and_get_lock_file_path(project_file: Path) -> Path | None:
    project_dir = project_file.parent
    if project_file.name == "package.json" and (project_dir / "package-lock.json").exists():
        subprocess.run(["npm", "install"], cwd=project_dir, check=True)
        click.echo(f"Updated package-lock.json in {project_dir}")
        return project_dir / "package-lock.json"

    if project_file.name == "pyproject.toml" and (project_dir / "uv.lock").exists():
        subprocess.run(["uv", "lock"], cwd=project_dir, check=True)
        click.echo(f"Updated uv.lock in {project_dir}")
        return project_dir / "uv.lock"

    if project_file.name == "pubspec.yaml" and (project_dir / "pubspec.lock").exists():
        subprocess.run(["dart", "pub", "get"], cwd=project_dir, check=True)
        click.echo(f"Updated pubspec.lock in {project_dir}")
        return project_dir / "pubspec.lock"

    return None


def _bump_version(version: str) -> str:
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _create_git_data_commit(
    repo_root: Path,
    repo,
    branch_name: str,
    base_sha: str,
    commit_message: str,
    edited_files: list[str],
) -> str:
    ref = repo.get_git_ref(f"heads/{branch_name}")
    if ref.object.sha != base_sha:
        raise click.ClickException(f"Pull request head changed unexpectedly: expected {base_sha}, found {ref.object.sha}.")

    base_commit = repo.get_git_commit(base_sha)
    tree_elements = []
    for relative_path in list(dict.fromkeys(edited_files)):
        absolute_path = repo_root / relative_path
        tree_elements.append(
            InputGitTreeElement(
                path=relative_path,
                mode="100644",
                type="blob",
                content=absolute_path.read_text(encoding="utf-8"),
            )
        )

    new_tree = repo.create_git_tree(tree=tree_elements, base_tree=base_commit.tree)
    new_commit = repo.create_git_commit(commit_message, new_tree, [base_commit])
    ref.edit(new_commit.sha, force=False)
    return new_commit.sha


@click.command()
def get() -> None:
    for project_file in ["pom.xml", "package.json", "pyproject.toml", "pubspec.yaml"]:
        path = Path(project_file)
        if path.exists():
            click.echo(_get_version_from_project_file(path), nl=False)
            return

    click.echo("No supported project file found.", nl=False)


@click.command(name="set-version")
@click.argument("version")
def set_version(version: str) -> None:
    updated = False

    for project_file in ["pom.xml", "package.json", "pyproject.toml", "pubspec.yaml"]:
        path = Path(project_file)
        if path.exists():
            _set_version_in_project_file(path, version)
            click.echo(f"Set {project_file} to version {version}")
            updated = True

    if not updated:
        click.echo("No supported project file found.")


@click.command()
@click.option("--expected-head-sha", default=None)
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path))
def bump(expected_head_sha: str | None, github_output: Path | None) -> None:
    repo_root = find_repo_root(Path("."))
    version_file = repo_root / "VERSION.txt"
    project_files = [
        repo_root / "lib/java/pom.xml",
        repo_root / "lib/py/pyproject.toml",
        repo_root / "lib/ts/package.json",
        repo_root / "bind/dart/pubspec.yaml",
        repo_root / "bind/dart/package.json",
        repo_root / "sdk/cli/pyproject.toml",
        repo_root / "sdk/prettier/package.json",
        repo_root / "sdk/console/package.json",
    ]

    github_token = require_env("GITHUB_TOKEN")
    github_repository = require_env("GITHUB_REPOSITORY")
    pr_number = int(require_env("PR_NUMBER"))

    repo = Github(github_token).get_repo(github_repository)
    pr = repo.get_pull(pr_number)
    head_sha = pr.head.sha
    head_ref = pr.head.ref

    if expected_head_sha and head_sha != expected_head_sha:
        raise click.ClickException(f"Pull request head changed unexpectedly: expected {expected_head_sha}, found {head_sha}.")

    if not version_file.exists():
        raise click.ClickException(f"Version file {version_file} does not exist.")

    version = version_file.read_text(encoding="utf-8").strip()
    new_version = _bump_version(version)
    version_file.write_text(new_version, encoding="utf-8")
    click.echo(f"Updated version file {version_file} to version {new_version}")

    edited_files = [_repo_relative_path(repo_root, version_file)]

    for project_file in project_files:
        if project_file.exists():
            _set_version_in_project_file(project_file, new_version)
            click.echo(f"Updated {project_file} to version {new_version}")
            edited_files.append(_repo_relative_path(repo_root, project_file))
        else:
            click.echo(f"Project file {project_file} does not exist.")

    for project_file in project_files:
        lock_file = _update_and_get_lock_file_path(project_file)
        if lock_file is not None:
            edited_files.append(_repo_relative_path(repo_root, lock_file))

    changed_paths = sorted({file.filename for file in pr.get_files()})
    release_manifest = compute_release_manifest(
        repo_root,
        changed_paths=changed_paths,
        version=new_version,
        pr_number=pr_number,
    )
    sorted_release_targets = list(release_manifest.targets)
    print(f"release_targets: {sorted_release_targets}")

    release_string = "Release targets:\n" + "\n".join(sorted_release_targets) if sorted_release_targets else "No release targets"

    manifest_path = write_release_manifest(repo_root, release_manifest)
    edited_files.append(_repo_relative_path(repo_root, manifest_path))
    click.echo(f"Updated {_repo_relative_path(repo_root, manifest_path)}")

    doc_versions_path = write_doc_versions(
        repo_root,
        None,
        pending_version=new_version,
        pending_targets=sorted_release_targets,
        existing_version_by_target=_read_existing_doc_versions(repo_root / "doc" / "04-operate" / "03-versions.md"),
    )
    edited_files.append(_repo_relative_path(repo_root, doc_versions_path))
    click.echo(f"Updated {_repo_relative_path(repo_root, doc_versions_path)}")

    new_commit_message = f"Bump version to {new_version} (#{pr_number})\n\n{release_string}"
    new_commit_sha = _create_git_data_commit(repo_root, repo, head_ref, head_sha, new_commit_message, edited_files)

    write_github_outputs(
        github_output,
        {
            "head_sha": new_commit_sha,
            "head_ref": head_ref,
            "version": new_version,
        },
    )
