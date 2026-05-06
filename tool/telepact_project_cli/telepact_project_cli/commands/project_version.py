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
from pathlib import Path

import click
import toml
from lxml import etree as ET
from ruamel.yaml import YAML

from ..release_plan import ReleaseComparison, compute_release_manifest_for_comparison, git_ref_comparison

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
    project_dir = Path(project_file).parent
    if project_file.endswith("package.json") and (project_dir / "package-lock.json").exists():
        subprocess.run(["npm", "install"], cwd=project_dir, check=True)
        click.echo(f"Updated package-lock.json in {project_dir}")
        return str(project_dir / "package-lock.json")

    if project_file.endswith("pyproject.toml") and (project_dir / "uv.lock").exists():
        subprocess.run(["uv", "lock"], cwd=project_dir, check=True)
        click.echo(f"Updated uv.lock in {project_dir}")
        return str(project_dir / "uv.lock")

    if project_file.endswith("pubspec.yaml") and (project_dir / "pubspec.lock").exists():
        subprocess.run(["dart", "pub", "get"], cwd=project_dir, check=True)
        click.echo(f"Updated pubspec.lock in {project_dir}")
        return str(project_dir / "pubspec.lock")

    return None


def _bump_version(version: str) -> str:
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)

def _release_comparison_since_main(main_ref: str = "origin/main") -> ReleaseComparison:
    return git_ref_comparison(Path("."), base_ref=main_ref, head_ref="HEAD", use_merge_base=True)


def create_version_bump_commit(
    pr_number: int | None = None,
    changed_paths: list[str] | None = None,
    *,
    compute_release_targets: bool = True,
) -> str:
    """Create the release bump commit for either an existing PR flow or a standalone bump PR."""
    version_file = "VERSION.txt"
    if not os.path.exists(version_file):
        raise click.ClickException(f"Version file {version_file} does not exist.")

    with open(version_file, "r") as f:
        version = f.read().strip()

    if compute_release_targets:
        comparison = _release_comparison_since_main()
        release_manifest = compute_release_manifest_for_comparison(
            Path("."),
            comparison=comparison,
            version=version,
            pr_number=pr_number,
        )
        sorted_release_targets = list(release_manifest.targets)
    else:
        sorted_release_targets = []

    new_version = version
    edited_files: list[str] = []

    if sorted_release_targets or not compute_release_targets:
        new_version = _bump_version(version)

        with open(version_file, "w") as f:
            f.write(new_version)

        click.echo(f"Updated version file {version_file} to version {new_version}")

        edited_files.append(version_file)

        for project_file in PROJECT_FILES:
            if os.path.exists(project_file):
                _set_version_in_project_file(project_file, new_version)
                click.echo(f"Updated {project_file} to version {new_version}")
                edited_files.append(project_file)
            else:
                click.echo(f"Project file {project_file} does not exist.")

        for project_file in PROJECT_FILES:
            lock_file = _update_and_get_lock_file_path(project_file)
            if lock_file is not None:
                edited_files.append(lock_file)

    if compute_release_targets:
        release_target_lines = "\n".join(sorted_release_targets) if sorted_release_targets else "(none)"
        new_commit_msg = f"Bump version to {new_version}\n\nRelease targets:\n{release_target_lines}"
    else:
        new_commit_msg = f"Bump version to {new_version}"

    subprocess.run(["git", "add"] + list(dict.fromkeys(edited_files)), check=True)
    subprocess.run(["git", "commit", "-m", new_commit_msg], check=True)
    return new_version


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
            _update_and_get_lock_file_path(project_file)
            click.echo(f"Set {project_file} to version {version}")
            updated = True

    if not updated:
        click.echo("No supported project file found.")


@click.command()
def bump() -> None:
    pr_number_str = os.getenv("PR_NUMBER")
    create_version_bump_commit(int(pr_number_str) if pr_number_str else None)
