#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

import os
import subprocess
from pathlib import Path

import click

LICENSE_HEADER_IGNORE_FILE = ".license-header-ignore"
APACHE_LICENSE_SPDX_IDENTIFIER = "SPDX-License-Identifier: Apache-2.0"


def _has_shebang(file_path: str) -> bool:
    with open(file_path, "r") as file:
        return file.readline().startswith("#!")


def _license_header_supported(file_path: str) -> bool:
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)

    return (
        (
            file_name != "pubspec.yaml"
            and file_extension in [".py", ".java", ".ts", ".tsx", ".dart", ".sh", ".js", ".mjs", ".go", ".rb", ".yaml", ".yml", ".html", ".css", ".svelte"]
        )
        or file_name == "Dockerfile"
        or file_name == "Makefile"
        or (not file_extension and _has_shebang(file_path))
    )


def _license_header_ignored(file_path: str) -> bool:
    path = Path(file_path)
    for directory in path.parents:
        if (directory / LICENSE_HEADER_IGNORE_FILE).exists():
            return True

    return False


def _get_comment_syntax(file_extension, file_name):
    if file_extension in [".py", ".sh", ".rb", ".yaml", ".yml"] or file_name == "Dockerfile" or file_name == "Makefile" or not file_extension:
        return "#|", ""
    elif file_extension in [".java", ".ts", ".tsx", ".dart", ".js", ".mjs", ".go"]:
        return "//|", ""
    elif file_extension in [".html", ".svelte"]:
        return "<!--|", "|-->"
    elif file_extension == ".css":
        return "/*|", "|*/"
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")


def _read_license_header(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    header_lines = []
    for line in lines:
        if "-------------------" in line.strip():
            break
        header_lines.append(line)

    while header_lines and not header_lines[-1].strip():
        header_lines.pop()

    source_header_lines = []
    spdx_identifier = None

    for line in header_lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("Copyright"):
            source_header_lines.append(f"{stripped_line}\n")
            continue
        if stripped_line.startswith("SPDX-License-Identifier:"):
            spdx_identifier = stripped_line

    if not source_header_lines:
        raise click.ClickException("License header source must include at least one copyright line.")

    source_header_lines.append(f"{spdx_identifier or APACHE_LICENSE_SPDX_IDENTIFIER}\n")
    return source_header_lines


def _update_file(file_path, license_header, start_comment_syntax, end_comment_syntax, file_extension) -> bool:
    with open(file_path, "r") as file:
        lines = file.readlines()

    original_content = "".join(lines)

    new_lines = []
    start_copying = False
    in_html_comment_block = False

    shebang = lines[0] if lines and lines[0].startswith("#!") else None

    for line in lines:
        if line.startswith("#!"):
            continue
        if start_copying:
            new_lines.append(line)
            continue
        if line.startswith(start_comment_syntax):
            continue
        if file_extension in [".html", ".svelte"]:
            stripped_line = line.lstrip()
            if in_html_comment_block:
                new_lines.append(line)
                if "-->" in stripped_line:
                    in_html_comment_block = False
                continue
            if stripped_line.startswith("<!--"):
                new_lines.append(line)
                if "-->" not in stripped_line:
                    in_html_comment_block = True
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

    with open(file_path, "w") as file:
        file.write(new_content)
    print(f"Re-written: {file_path}")

    return True


@click.command()
@click.argument("license_header_path")
def license_header(license_header_path):
    license_header_lines = _read_license_header(license_header_path)
    cli_command = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE, text=True)
    files = cli_command.stdout.splitlines()

    updated_files = 0
    for file_path in files:
        if _license_header_ignored(file_path):
            continue
        if not _license_header_supported(file_path):
            continue

        file_extension = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        start_comment_syntax, end_comment_syntax = _get_comment_syntax(file_extension, file_name)
        updated = _update_file(file_path, license_header_lines, start_comment_syntax, end_comment_syntax, file_extension)
        if updated:
            updated_files += 1

    if updated_files == 0:
        print("All files are up-to-date.")
