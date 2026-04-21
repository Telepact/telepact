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

import subprocess
from pathlib import Path

import click

from ..constants import PROJECT_FILES
from ..git_helpers import git_lines, require_int_env
from ..project_files import (
    find_supported_project_file,
    iter_supported_project_files,
    read_version,
    update_lock_files,
    write_version,
)
from ..release_plan import compute_release_manifest, find_repo_root, write_release_manifest
from .doc_versions import write_doc_versions


def _bump_patch_version(version: str) -> str:
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def _deduplicate_preserving_order(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


@click.command()
def get() -> None:
    project_file = find_supported_project_file(Path("."))
    if project_file is None:
        click.echo("No supported project file found.", nl=False)
        return

    click.echo(read_version(project_file), nl=False)


@click.command()
@click.argument("version")
def set_version(version: str) -> None:
    updated = False

    for project_file in iter_supported_project_files(Path(".")):
        write_version(project_file, version)
        click.echo(f"Set {project_file.name} to version {version}")
        updated = True

    if not updated:
        click.echo("No supported project file found.")


@click.command()
def bump() -> None:
    repo_root = find_repo_root(Path("."))
    pr_number = require_int_env("PR_NUMBER")
    prev_commit_paths = git_lines(["show", "--name-only", "--pretty=format:", "HEAD"], cwd=repo_root)

    version_file = repo_root / "VERSION.txt"
    if not version_file.exists():
        click.echo(f"Version file {version_file} does not exist.")
        return

    new_version = _bump_patch_version(version_file.read_text(encoding="utf-8").strip())
    version_file.write_text(new_version, encoding="utf-8")
    click.echo(f"Updated version file VERSION.txt to version {new_version}")

    edited_files = ["VERSION.txt"]

    for project_file_name in PROJECT_FILES:
        project_file = repo_root / project_file_name
        if project_file.exists():
            write_version(project_file, new_version)
            click.echo(f"Updated {project_file_name} to version {new_version}")
            edited_files.append(project_file_name)
            for lock_file in update_lock_files(project_file):
                lock_file_name = lock_file.relative_to(repo_root).as_posix()
                edited_files.append(lock_file_name)
                click.echo(f"Updated {lock_file_name}")
        else:
            click.echo(f"Project file {project_file_name} does not exist.")

    release_manifest = compute_release_manifest(
        repo_root,
        changed_paths=prev_commit_paths,
        version=new_version,
        pr_number=pr_number,
    )
    release_targets = list(release_manifest.targets)
    release_string = "Release targets:\n" + "\n".join(release_targets) if release_targets else "No release targets"

    manifest_path = write_release_manifest(repo_root, release_manifest)
    manifest_file_name = manifest_path.relative_to(repo_root).as_posix()
    edited_files.append(manifest_file_name)
    click.echo(f"Updated {manifest_file_name}")

    doc_versions_path = write_doc_versions(
        repo_root,
        None,
        pending_version=new_version,
        pending_targets=release_targets,
    )
    doc_versions_file_name = doc_versions_path.relative_to(repo_root).as_posix()
    edited_files.append(doc_versions_file_name)
    click.echo(f"Updated {doc_versions_file_name}")

    commit_message = f"Bump version to {new_version} (#{pr_number})\n\n{release_string}"
    unique_files = _deduplicate_preserving_order(edited_files)
    subprocess.run(["git", "add", *unique_files], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_root, check=True)
