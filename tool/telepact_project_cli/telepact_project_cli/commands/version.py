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
import subprocess
import sys
from pathlib import Path

import click

from ..project_files import find_supported_project_files, read_project_version, write_project_version
from ..release_plan import compute_release_manifest, write_release_manifest
from .doc_versions import write_doc_versions

VERSIONED_PROJECT_FILES = (
    Path("lib/java/pom.xml"),
    Path("lib/py/pyproject.toml"),
    Path("lib/ts/package.json"),
    Path("bind/dart/pubspec.yaml"),
    Path("bind/dart/package.json"),
    Path("sdk/cli/pyproject.toml"),
    Path("sdk/prettier/package.json"),
    Path("sdk/console/package.json"),
)


def bump_version(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"


@click.command()
def get() -> None:
    project_files = find_supported_project_files()
    if not project_files:
        click.echo("No supported project file found.", nl=False)
        return

    click.echo(read_project_version(project_files[0]), nl=False)


@click.command()
@click.argument("version")
def set_version(version: str) -> None:
    updated = False

    for project_file in find_supported_project_files():
        write_project_version(project_file, version)
        click.echo(f"Set {project_file.name} to version {version}")
        updated = True

    if not updated:
        click.echo("No supported project file found.")


@click.command()
def bump() -> None:
    version_file = Path("VERSION.txt")
    pr_number = _required_int_env("PR_NUMBER")

    prev_commit_paths = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.splitlines()

    print("prev_commit_paths:")
    print(prev_commit_paths)

    if not version_file.exists():
        click.echo(f"Version file {version_file} does not exist.")
        return

    version = version_file.read_text(encoding="utf-8").strip()
    new_version = bump_version(version)
    version_file.write_text(new_version, encoding="utf-8")
    click.echo(f"Updated version file {version_file} to version {new_version}")

    edited_files: list[str] = [str(version_file)]

    for project_file in VERSIONED_PROJECT_FILES:
        if project_file.exists():
            write_project_version(project_file, new_version)
            click.echo(f"Updated {project_file} to version {new_version}")
            edited_files.append(str(project_file))
        else:
            click.echo(f"Project file {project_file} does not exist.")

    _update_lock_files(VERSIONED_PROJECT_FILES, edited_files)

    release_manifest = compute_release_manifest(
        Path("."),
        changed_paths=prev_commit_paths,
        version=new_version,
        pr_number=pr_number,
    )
    sorted_release_targets = list(release_manifest.targets)
    print(f"release_targets: {sorted_release_targets}")

    if sorted_release_targets:
        release_string = "Release targets:\n" + "\n".join(sorted_release_targets)
    else:
        release_string = "No release targets"

    manifest_path = write_release_manifest(Path("."), release_manifest)
    repo_relative_manifest_path = os.path.relpath(manifest_path, Path.cwd())
    edited_files.append(repo_relative_manifest_path)
    click.echo(f"Updated {repo_relative_manifest_path}")

    doc_versions_path = write_doc_versions(
        Path("."),
        None,
        pending_version=new_version,
        pending_targets=sorted_release_targets,
    )
    repo_relative_doc_versions_path = os.path.relpath(doc_versions_path, Path.cwd())
    edited_files.append(repo_relative_doc_versions_path)
    click.echo(f"Updated {repo_relative_doc_versions_path}")

    new_commit_msg = f"Bump version to {new_version} (#{pr_number})\n\n" + release_string
    subprocess.run(["git", "add", *list(dict.fromkeys(edited_files))], check=True)
    subprocess.run(["git", "commit", "-m", new_commit_msg], check=True)


def _required_int_env(name: str) -> int:
    value = os.getenv(name)
    if not value:
        click.echo(f"{name} environment variable not set.", err=True)
        sys.exit(1)
    return int(value)


def _update_lock_files(project_files: tuple[Path, ...], edited_files: list[str]) -> None:
    for project_file in project_files:
        project_directory = project_file.parent

        if project_file.name == "package.json" and (project_directory / "package-lock.json").exists():
            subprocess.run(["npm", "install"], cwd=project_directory, check=True)
            edited_files.append(str(project_directory / "package-lock.json"))
            click.echo(f"Updated package-lock.json in {project_directory}")

        if project_file.name == "pyproject.toml" and (project_directory / "uv.lock").exists():
            subprocess.run(["uv", "lock"], cwd=project_directory, check=True)
            edited_files.append(str(project_directory / "uv.lock"))
            click.echo(f"Updated uv.lock in {project_directory}")

        if project_file.name == "pubspec.yaml" and (project_directory / "pubspec.lock").exists():
            subprocess.run(["dart", "pub", "get"], cwd=project_directory, check=True)
            edited_files.append(str(project_directory / "pubspec.lock"))
            click.echo(f"Updated pubspec.lock in {project_directory}")
