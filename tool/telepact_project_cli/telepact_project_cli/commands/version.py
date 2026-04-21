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

from ..project_files import (
    bump_version,
    find_local_project_file,
    iter_local_project_files,
    read_project_version,
    refresh_lock_file,
    write_project_version,
)
from ..release_plan import compute_release_manifest, write_release_manifest
from .doc_versions import write_doc_versions

VERSION_FILE = Path("VERSION.txt")
MONOREPO_PROJECT_FILES = (
    Path("lib/java/pom.xml"),
    Path("lib/py/pyproject.toml"),
    Path("lib/ts/package.json"),
    Path("bind/dart/pubspec.yaml"),
    Path("bind/dart/package.json"),
    Path("sdk/cli/pyproject.toml"),
    Path("sdk/prettier/package.json"),
    Path("sdk/console/package.json"),
)


def _require_pr_number() -> int:
    pr_number_str = os.getenv("PR_NUMBER")
    if not pr_number_str:
        click.echo("PR_NUMBER environment variable not set.", err=True)
        sys.exit(1)
    return int(pr_number_str)


def _head_changed_paths() -> list[str]:
    output = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout
    return [path for path in output.strip().splitlines() if path]


def _read_repo_version(version_file: Path = VERSION_FILE) -> str:
    if not version_file.exists():
        click.echo(f"Version file {version_file} does not exist.")
        raise click.Abort()
    return version_file.read_text(encoding="utf-8").strip()


def _write_repo_version(version_file: Path, version: str) -> None:
    version_file.write_text(version, encoding="utf-8")


def _update_project_files(project_files: tuple[Path, ...], version: str) -> list[str]:
    edited_files: list[str] = []
    for project_file in project_files:
        if project_file.exists():
            write_project_version(project_file, version)
            click.echo(f"Updated {project_file.as_posix()} to version {version}")
            edited_files.append(project_file.as_posix())
        else:
            click.echo(f"Project file {project_file.as_posix()} does not exist.")
    return edited_files


def _refresh_lock_files(project_files: tuple[Path, ...]) -> list[str]:
    edited_files: list[str] = []
    for project_file in project_files:
        lock_file = refresh_lock_file(project_file)
        if lock_file is None:
            continue
        edited_files.append(lock_file.as_posix())
        click.echo(f"Updated {lock_file.name} in {project_file.parent.as_posix()}")
    return edited_files


def _write_release_outputs(new_version: str, pr_number: int, changed_paths: list[str]) -> list[str]:
    release_manifest = compute_release_manifest(
        Path("."),
        changed_paths=changed_paths,
        version=new_version,
        pr_number=pr_number,
    )
    sorted_release_targets = list(release_manifest.targets)
    click.echo(f"release_targets: {sorted_release_targets}")

    manifest_path = write_release_manifest(Path("."), release_manifest)
    repo_relative_manifest_path = os.path.relpath(manifest_path, Path.cwd())
    click.echo(f"Updated {repo_relative_manifest_path}")

    doc_versions_path = write_doc_versions(
        Path("."),
        None,
        pending_version=new_version,
        pending_targets=sorted_release_targets,
    )
    repo_relative_doc_versions_path = os.path.relpath(doc_versions_path, Path.cwd())
    click.echo(f"Updated {repo_relative_doc_versions_path}")

    return [
        repo_relative_manifest_path,
        repo_relative_doc_versions_path,
        *sorted_release_targets,
    ]


def _commit_bump(edited_files: list[str], new_version: str, pr_number: int, release_targets: list[str]) -> None:
    if release_targets:
        release_string = "Release targets:\n" + "\n".join(release_targets)
    else:
        release_string = "No release targets"

    new_commit_msg = f"Bump version to {new_version} (#{pr_number})\n\n" + release_string
    subprocess.run(["git", "add", *list(dict.fromkeys(edited_files))], check=True)
    subprocess.run(["git", "commit", "-m", new_commit_msg], check=True)


@click.command()
def get() -> None:
    project_file = find_local_project_file(Path("."))
    if project_file is None:
        click.echo("No supported project file found.", nl=False)
        return
    click.echo(read_project_version(project_file), nl=False)


@click.command()
@click.argument("version")
def set_version(version: str) -> None:
    project_files = iter_local_project_files(Path("."))
    if not project_files:
        click.echo("No supported project file found.")
        return

    for project_file in project_files:
        write_project_version(project_file, version)
        click.echo(f"Set {project_file.name} to version {version}")


@click.command()
def bump() -> None:
    pr_number = _require_pr_number()
    prev_commit_paths = _head_changed_paths()

    click.echo("prev_commit_paths:")
    click.echo(str(prev_commit_paths))

    version = _read_repo_version(VERSION_FILE)
    new_version = bump_version(version)
    _write_repo_version(VERSION_FILE, new_version)
    click.echo(f"Updated version file {VERSION_FILE} to version {new_version}")

    edited_files = [VERSION_FILE.as_posix()]
    edited_files.extend(_update_project_files(MONOREPO_PROJECT_FILES, new_version))
    edited_files.extend(_refresh_lock_files(MONOREPO_PROJECT_FILES))

    release_outputs = _write_release_outputs(new_version, pr_number, prev_commit_paths)
    edited_files.extend(release_outputs[:2])
    _commit_bump(edited_files, new_version, pr_number, release_outputs[2:])
