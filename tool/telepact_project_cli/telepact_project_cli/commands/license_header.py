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

import subprocess
from pathlib import Path

import click

LICENSE_HEADER_IGNORE_FILE = ".license-header-ignore"


@click.command()
@click.argument("license_header_path")
def license_header(license_header_path: str) -> None:
    license_header_lines = _read_license_header(Path(license_header_path))
    files = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE, text=True, check=True).stdout.splitlines()

    updated_files = 0
    for file_path in files:
        if _license_header_ignored(file_path) or not _license_header_supported(file_path):
            continue

        start_comment_syntax, end_comment_syntax = _comment_syntax(file_path)
        if _update_file(Path(file_path), license_header_lines, start_comment_syntax, end_comment_syntax):
            updated_files += 1

    if updated_files == 0:
        print("All files are up-to-date.")


def _license_header_supported(file_path: str) -> bool:
    path = Path(file_path)
    return (
        (path.name != "pubspec.yaml" and path.suffix.lower() in [".py", ".java", ".ts", ".dart", ".sh", ".js", ".yaml", ".yml", ".html", ".css", ".svelte"])
        or path.name == "Dockerfile"
        or path.name == "Makefile"
    )


def _license_header_ignored(file_path: str) -> bool:
    path = Path(file_path)
    for directory in path.parents:
        if (directory / LICENSE_HEADER_IGNORE_FILE).exists():
            return True
    return False


def _comment_syntax(file_path: str) -> tuple[str, str]:
    path = Path(file_path)
    if path.suffix.lower() in [".py", ".sh", ".yaml", ".yml"] or path.name in {"Dockerfile", "Makefile"}:
        return "#|", ""
    if path.suffix.lower() in [".java", ".ts", ".dart", ".js"]:
        return "//|", ""
    if path.suffix.lower() in [".html", ".svelte"]:
        return "<!--|", "|-->"
    if path.suffix.lower() == ".css":
        return "/*|", "|*/"
    raise ValueError(f"Unsupported file extension: {path.suffix}")


def _read_license_header(file_path: Path) -> list[str]:
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)

    header_lines: list[str] = []
    for line in lines:
        if "-------------------" in line.strip():
            break
        header_lines.append(line)

    while header_lines and not header_lines[-1].strip():
        header_lines.pop()

    return header_lines


def _update_file(file_path: Path, license_header: list[str], start_comment_syntax: str, end_comment_syntax: str) -> bool:
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    original_content = "".join(lines)

    new_lines: list[str] = []
    start_copying = False
    shebang = lines[0] if lines and lines[0].startswith("#!") else None

    for line in lines:
        if line.startswith("#!"):
            continue
        if start_copying:
            new_lines.append(line)
            continue
        if line.startswith(start_comment_syntax):
            continue
        if line.strip() == "":
            continue
        new_lines.append(line)
        start_copying = True

    max_length = max(len(line.strip()) for line in license_header) + 2
    license_text = "".join(
        f"{start_comment_syntax}  {line.strip().ljust(max_length)}{end_comment_syntax}".strip() + "\n"
        for line in license_header
    )

    new_banner = ""
    if shebang:
        new_banner += shebang
        new_banner += "\n"

    new_banner += f"{start_comment_syntax}  {''.ljust(max_length)}{end_comment_syntax}".strip() + "\n"
    new_banner += f"{license_text.strip()}\n"
    new_banner += f"{start_comment_syntax}  {''.ljust(max_length)}{end_comment_syntax}".strip() + "\n\n"

    new_content = new_banner + "".join(new_lines)
    if new_content == original_content:
        return False

    file_path.write_text(new_content, encoding="utf-8")
    print(f"Re-written: {file_path}")
    return True
