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
import subprocess
from pathlib import Path

import click
import toml
from lxml import etree as ET
from ruamel.yaml import YAML

yaml = YAML()

SUPPORTED_VERSION_FILES = ("pom.xml", "package.json", "pyproject.toml", "pubspec.yaml")
_MAVEN_VERSION_XPATH = "{http://maven.apache.org/POM/4.0.0}version"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_pyproject(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return toml.load(file)


def project_version(data: dict) -> str:
    project = data.get("project", {})
    if "version" in project:
        return project["version"]
    return data["tool"]["poetry"]["version"]


def set_project_version_data(data: dict, version: str) -> dict:
    project = data.get("project")
    if isinstance(project, dict) and "version" in project:
        project["version"] = version
        return data

    data["tool"]["poetry"]["version"] = version
    return data


def find_supported_project_file(base_dir: Path = Path(".")) -> Path | None:
    for file_name in SUPPORTED_VERSION_FILES:
        path = base_dir / file_name
        if path.exists():
            return path
    return None


def iter_supported_project_files(base_dir: Path = Path(".")) -> list[Path]:
    return [base_dir / file_name for file_name in SUPPORTED_VERSION_FILES if (base_dir / file_name).exists()]


def _pom_version_element(path: Path):
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(str(path), parser)
    root = tree.getroot()
    version_element = root.find(_MAVEN_VERSION_XPATH)
    if version_element is None or version_element.text is None:
        raise click.ClickException(f"Missing Maven version in {path}")
    return tree, version_element


def read_version(path: Path) -> str:
    if path.name == "pom.xml":
        _, version_element = _pom_version_element(path)
        return version_element.text
    if path.name == "package.json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data["version"]
    if path.name == "pyproject.toml":
        return project_version(load_pyproject(path))
    if path.name == "pubspec.yaml":
        with path.open("r", encoding="utf-8") as file:
            data = yaml.load(file)
        return data["version"]
    raise click.ClickException(f"Unsupported project file type: {path}")


def write_version(path: Path, version: str) -> None:
    if path.name == "pom.xml":
        tree, version_element = _pom_version_element(path)
        version_element.text = version
        tree.write(str(path), xml_declaration=True, encoding="utf-8", pretty_print=True)
        return

    if path.name == "package.json":
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = version
        write_json(path, data)
        return

    if path.name == "pyproject.toml":
        data = set_project_version_data(load_pyproject(path), version)
        with path.open("w", encoding="utf-8") as file:
            toml.dump(data, file)
        return

    if path.name == "pubspec.yaml":
        with path.open("r", encoding="utf-8") as file:
            data = yaml.load(file)
        data["version"] = version
        with path.open("w", encoding="utf-8") as file:
            yaml.dump(data, file)
        return

    raise click.ClickException(f"Unsupported project file type: {path}")


def update_lock_files(project_file: Path) -> list[Path]:
    directory = project_file.parent
    updated_files: list[Path] = []

    if project_file.name == "package.json":
        lock_file = directory / "package-lock.json"
        if lock_file.exists():
            subprocess.run(["npm", "install"], cwd=directory, check=True)
            updated_files.append(lock_file)

    if project_file.name == "pyproject.toml":
        lock_file = directory / "uv.lock"
        if lock_file.exists():
            subprocess.run(["uv", "lock"], cwd=directory, check=True)
            updated_files.append(lock_file)

    if project_file.name == "pubspec.yaml":
        lock_file = directory / "pubspec.lock"
        if lock_file.exists():
            subprocess.run(["dart", "pub", "get"], cwd=directory, check=True)
            updated_files.append(lock_file)

    return updated_files
