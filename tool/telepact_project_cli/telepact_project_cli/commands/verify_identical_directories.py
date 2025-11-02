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

import filecmp
from pathlib import Path
from typing import Dict, Iterable

import click


def _format_errors(errors: Iterable[str]) -> str:
    return "\n".join(errors)


def _verify_directories(source_dir: Path, target_dir: Path) -> None:
    errors: list[str] = []

    source_files = _collect_files(source_dir)
    target_files = _collect_files(target_dir)

    missing_in_target = sorted(set(source_files) - set(target_files))
    if missing_in_target:
        for rel_path in missing_in_target:
            errors.append(
                f"Missing file in target directory: {target_dir / rel_path} (copy from source)"
            )

    missing_in_source = sorted(set(target_files) - set(source_files))
    if missing_in_source:
        for rel_path in missing_in_source:
            errors.append(
                f"Extra file in target directory: {target_dir / rel_path} (remove or sync)"
            )

    for rel_path in sorted(set(source_files) & set(target_files)):
        src = source_files[rel_path]
        dst = target_files[rel_path]
        if not filecmp.cmp(src, dst, shallow=False):
            errors.append(
                f"File contents differ for {rel_path} (sync directories to resolve)"
            )

    if errors:
        raise click.ClickException(_format_errors(errors))

    click.echo("Directories are identical.")


@click.command(name="verify-identical-directories")
@click.argument(
    "source_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.argument(
    "target_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def verify_identical_directories(source_dir: Path, target_dir: Path) -> None:
    """Ensure both directories contain the same files with identical contents."""

    _verify_directories(source_dir, target_dir)


def _collect_files(root: Path) -> Dict[Path, Path]:
    files: Dict[Path, Path] = {}
    for path in root.rglob("*"):
        if path.is_file():
            files[path.relative_to(root)] = path
    return files
