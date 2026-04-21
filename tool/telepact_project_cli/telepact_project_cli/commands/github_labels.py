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

import click
from github import Github

from ..constants import PROJECT_LABEL_MAP
from ..git_helpers import require_env, require_int_env


def _get_modified_files(base_branch: str, head_sha: str) -> str:
    try:
        subprocess.run(["git", "fetch", "origin", base_branch], check=True)
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_branch}", head_sha],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        click.echo(f"Error fetching or diffing: {exc}")
        return ""
    return result.stdout.strip()


def _get_modified_project_labels(files: str) -> set[str]:
    tags: set[str] = set()
    for file_name in files.split():
        for directory, tag in PROJECT_LABEL_MAP.items():
            if file_name.startswith(directory):
                tags.add(tag)
    return tags


@click.command()
def github_labels() -> None:
    token = require_env("GITHUB_TOKEN")
    repository = require_env("GITHUB_REPOSITORY")
    pr_number = require_int_env("PR_NUMBER")
    base_branch = require_env("BASE_BRANCH")
    head_sha = require_env("HEAD_SHA")

    files = _get_modified_files(base_branch, head_sha)
    click.echo(f"Modified files: {files}")

    github_client = Github(token)
    repo = github_client.get_repo(repository)
    pr = repo.get_pull(pr_number)
    current_labels = {label.name for label in pr.get_labels()}
    new_labels = _get_modified_project_labels(files)

    click.echo(f"Labels to be added: {new_labels}")

    added_labels: list[str] = []
    removed_labels: list[str] = []

    for label in new_labels:
        if label not in current_labels:
            pr.add_to_labels(label)
            added_labels.append(label)

    for label in current_labels:
        if label not in new_labels and label in PROJECT_LABEL_MAP.values():
            pr.remove_from_labels(label)
            removed_labels.append(label)

    click.echo(
        "Summary:\n"
        f"  Added tags: {', '.join(added_labels) if added_labels else 'None'}\n"
        f"  Removed tags: {', '.join(removed_labels) if removed_labels else 'None'}"
    )
