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
import subprocess
from pathlib import Path

from lxml import etree as ET
import toml
from ruamel.yaml import YAML

yaml = YAML()

SUPPORTED_PROJECT_FILE_NAMES = (
    "pom.xml",
    "package.json",
    "pyproject.toml",
    "pubspec.yaml",
)


def write_json(path: Path | str, data: dict) -> None:
    path = Path(path)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_pyproject(path: Path | str) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return toml.load(f)


def project_version(data: dict) -> str:
    project = data.get("project", {})
    if "version" in project:
        return project["version"]
    return data["tool"]["poetry"]["version"]


def set_project_version(data: dict, version: str) -> dict:
    project = data.get("project")
    if isinstance(project, dict) and "version" in project:
        project["version"] = version
        return data

    data["tool"]["poetry"]["version"] = version
    return data


def bump_version(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"


def find_local_project_file(base_path: Path | str = ".") -> Path | None:
    base_path = Path(base_path)
    for file_name in SUPPORTED_PROJECT_FILE_NAMES:
        candidate = base_path / file_name
        if candidate.exists():
            return candidate
    return None


def iter_local_project_files(base_path: Path | str = ".") -> list[Path]:
    base_path = Path(base_path)
    return [candidate for file_name in SUPPORTED_PROJECT_FILE_NAMES if (candidate := base_path / file_name).exists()]


def read_project_version(project_file: Path | str) -> str:
    project_file = Path(project_file)
    if project_file.name == "pom.xml":
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(str(project_file), parser)
        root = tree.getroot()
        version = root.find("{http://maven.apache.org/POM/4.0.0}version")
        if version is None or version.text is None:
            raise ValueError(f"Unable to find version in {project_file}")
        return version.text

    if project_file.name == "package.json":
        with project_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data["version"]

    if project_file.name == "pyproject.toml":
        return project_version(load_pyproject(project_file))

    if project_file.name == "pubspec.yaml":
        with project_file.open("r", encoding="utf-8") as f:
            data = yaml.load(f)
        return data["version"]

    raise ValueError(f"Unsupported project file: {project_file}")


def write_project_version(project_file: Path | str, version: str) -> None:
    project_file = Path(project_file)
    if project_file.name == "pom.xml":
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(str(project_file), parser)
        root = tree.getroot()
        version_node = root.find("{http://maven.apache.org/POM/4.0.0}version")
        if version_node is None:
            raise ValueError(f"Unable to find version in {project_file}")
        version_node.text = version
        tree.write(str(project_file), xml_declaration=True, encoding="utf-8", pretty_print=True)
        return

    if project_file.name == "package.json":
        with project_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data["version"] = version
        write_json(project_file, data)
        return

    if project_file.name == "pyproject.toml":
        data = set_project_version(load_pyproject(project_file), version)
        with project_file.open("w", encoding="utf-8") as f:
            toml.dump(data, f)
        return

    if project_file.name == "pubspec.yaml":
        with project_file.open("r", encoding="utf-8") as f:
            data = yaml.load(f)
        data["version"] = version
        with project_file.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)
        return

    raise ValueError(f"Unsupported project file: {project_file}")


def refresh_lock_file(project_file: Path | str) -> Path | None:
    project_file = Path(project_file)
    if project_file.name == "package.json":
        lock_path = project_file.parent / "package-lock.json"
        if lock_path.exists():
            subprocess.run(["npm", "install"], cwd=project_file.parent, check=True)
            return lock_path
        return None

    if project_file.name == "pyproject.toml":
        lock_path = project_file.parent / "uv.lock"
        if lock_path.exists():
            subprocess.run(["uv", "lock"], cwd=project_file.parent, check=True)
            return lock_path
        return None

    if project_file.name == "pubspec.yaml":
        lock_path = project_file.parent / "pubspec.lock"
        if lock_path.exists():
            subprocess.run(["dart", "pub", "get"], cwd=project_file.parent, check=True)
            return lock_path
        return None

    return None
