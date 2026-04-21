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

import click
from pathlib import Path

from .commands.consolidated_readme import consolidated_readme
from .commands.doc_versions import doc_versions
from .commands.github_workflow import automerge, github_labels, publish_targets, release
from .commands.license_header import license_header
from .commands.version import bump, get, set_version


@click.group()
def main() -> None:
    pass


@click.command()
@click.option('--add', 'add_name', help='Add a name to .gitignore')
@click.option('--remove', 'remove_name', help='Remove a name from .gitignore')
def gitignore(add_name, remove_name):
    """Add or remove entries in .gitignore"""
    if add_name and remove_name:
        raise click.UsageError("Cannot use --add and --remove at the same time.")
    if not add_name and not remove_name:
        raise click.UsageError("Must provide either --add or --remove.")

    gitignore_path = Path('.gitignore')

    if not gitignore_path.exists():
        if remove_name:
            return  # Nothing to remove
        if add_name:
            gitignore_path.touch()

    lines = gitignore_path.read_text().splitlines()
    name = add_name or remove_name

    if add_name:
        if name not in lines:
            existing_text = gitignore_path.read_text(encoding="utf-8")
            prefix = "" if not existing_text or existing_text.endswith("\n") else "\n"
            with gitignore_path.open("a", encoding="utf-8") as f:
                f.write(f"{prefix}{name}\n")
    elif remove_name:
        if name in lines:
            new_lines = [line for line in lines if line != name]
            if new_lines:
                gitignore_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            else:
                gitignore_path.write_text("", encoding="utf-8")

main.add_command(get)
main.add_command(set_version)
main.add_command(bump)
main.add_command(license_header)
main.add_command(github_labels)
main.add_command(release)
main.add_command(publish_targets)
main.add_command(automerge)
main.add_command(gitignore)
main.add_command(consolidated_readme)
main.add_command(doc_versions)

if __name__ == "__main__":
    main()
