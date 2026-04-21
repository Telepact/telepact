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
from pathlib import Path

import click

LICENSE_HEADER_IGNORE_FILE = ".license-header-ignore"


def license_header_supported(file_path: str) -> bool:
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)

    return (
        (file_name != "pubspec.yaml" and file_extension in [".py", ".java", ".ts", ".dart", ".sh", ".js", ".yaml", ".yml", ".html", ".css", ".svelte"])
        or file_name == "Dockerfile"
        or file_name == "Makefile"
    )


def license_header_ignored(file_path: str) -> bool:
    path = Path(file_path)
    for directory in path.parents:
        if (directory / LICENSE_HEADER_IGNORE_FILE).exists():
            return True
    return False


def get_comment_syntax(file_extension: str, file_name: str) -> tuple[str, str]:
    if file_extension in [".py", ".sh", ".yaml", ".yml"] or file_name == "Dockerfile" or file_name == "Makefile":
        return "#|", ""
    if file_extension in [".java", ".ts", ".dart", ".js"]:
        return "//|", ""
    if file_extension in [".html", ".svelte"]:
        return "<!--|", "|-->"
    if file_extension == ".css":
        return "/*|", "|*/"
    raise ValueError(f"Unsupported file extension: {file_extension}")


def read_license_header(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    header_lines = []
    for line in lines:
        if "-------------------" in line.strip():
            break
        header_lines.append(line)

    while header_lines and not header_lines[-1].strip():
        header_lines.pop()

    return header_lines


def update_file(file_path: str, license_header: list[str], start_comment_syntax: str, end_comment_syntax: str) -> bool:
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    original_content = "".join(lines)
    new_lines = []
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
        [f"{start_comment_syntax}  {line.strip().ljust(max_length)}{end_comment_syntax}".strip() + "\n" for line in license_header]
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

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)
    print(f"Re-written: {file_path}")
    return True


def apply_license_header(license_header_path: str) -> int:
    license_header_lines = read_license_header(license_header_path)
    cli_command = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE, text=True, check=True)
    files = cli_command.stdout.splitlines()

    updated_files = 0
    for file_path in files:
        if license_header_ignored(file_path):
            continue
        if not license_header_supported(file_path):
            continue

        file_extension = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        start_comment_syntax, end_comment_syntax = get_comment_syntax(file_extension, file_name)
        updated = update_file(file_path, license_header_lines, start_comment_syntax, end_comment_syntax)
        if updated:
            updated_files += 1
    return updated_files


@click.command(name="license-header")
@click.argument("license_header_path")
def license_header(license_header_path: str) -> None:
    updated_files = apply_license_header(license_header_path)
    if updated_files == 0:
        print("All files are up-to-date.")
