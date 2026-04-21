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
from pathlib import Path

import click
from lxml import etree as ET
from ruamel.yaml import YAML
import toml

yaml = YAML()

SUPPORTED_PROJECT_FILE_NAMES = ("pom.xml", "package.json", "pyproject.toml", "pubspec.yaml")
_MAVEN_VERSION_PATH = "{http://maven.apache.org/POM/4.0.0}version"


def find_supported_project_files(root: Path | str = ".") -> list[Path]:
    directory = Path(root)
    return [directory / name for name in SUPPORTED_PROJECT_FILE_NAMES if (directory / name).exists()]


def read_project_version(project_file: Path | str) -> str:
    path = Path(project_file)

    if path.name == "pom.xml":
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(str(path), parser)
        root = tree.getroot()
        version = root.findtext(_MAVEN_VERSION_PATH)
        if not version:
            raise click.ClickException(f"Missing Maven version in {path}")
        return version

    if path.name == "package.json":
        data = _read_json(path)
        version = data.get("version")
        if not isinstance(version, str) or not version:
            raise click.ClickException(f"Missing version in {path}")
        return version

    if path.name == "pyproject.toml":
        return _project_version(_read_pyproject(path), path)

    if path.name == "pubspec.yaml":
        data = _read_yaml(path)
        version = data.get("version")
        if not isinstance(version, str) or not version:
            raise click.ClickException(f"Missing version in {path}")
        return version

    raise click.ClickException(f"Unsupported project file: {path}")


def write_project_version(project_file: Path | str, version: str) -> None:
    path = Path(project_file)

    if path.name == "pom.xml":
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(str(path), parser)
        root = tree.getroot()
        node = root.find(_MAVEN_VERSION_PATH)
        if node is None:
            raise click.ClickException(f"Missing Maven version in {path}")
        node.text = version
        tree.write(str(path), xml_declaration=True, encoding="utf-8", pretty_print=True)
        return

    if path.name == "package.json":
        data = _read_json(path)
        data["version"] = version
        _write_json(path, data)
        return

    if path.name == "pyproject.toml":
        data = _set_project_version(_read_pyproject(path), version)
        with path.open("w", encoding="utf-8") as file:
            toml.dump(data, file)
        return

    if path.name == "pubspec.yaml":
        data = _read_yaml(path)
        data["version"] = version
        with path.open("w", encoding="utf-8") as file:
            yaml.dump(data, file)
        return

    raise click.ClickException(f"Unsupported project file: {path}")


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        file.write(json.dumps(data, indent=2) + "\n")


def _read_pyproject(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return toml.load(file)


def _project_version(data: dict, path: Path) -> str:
    project = data.get("project", {})
    version = project.get("version")
    if isinstance(version, str) and version:
        return version

    poetry = data.get("tool", {}).get("poetry", {})
    version = poetry.get("version")
    if isinstance(version, str) and version:
        return version

    raise click.ClickException(f"Missing version in {path}")


def _set_project_version(data: dict, version: str) -> dict:
    project = data.get("project")
    if isinstance(project, dict) and "version" in project:
        project["version"] = version
        return data

    data["tool"]["poetry"]["version"] = version
    return data


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.load(file)
    if not isinstance(data, dict):
        raise click.ClickException(f"Invalid YAML document in {path}")
    return data
