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
from github import Github

from ..constants import AUTOMERGE_ALLOWED_AUTHORS, AUTOMERGE_ALLOWED_FILES
from ..git_helpers import require_env, require_int_env


@click.command()
def automerge() -> None:
    """
    Approves and squashes a Pull Request if the author is on the hardcoded allow list.
    All necessary information is retrieved from environment variables.
    """
    pr_number = require_int_env("PR_NUMBER")
    github_token = require_env("GITHUB_TOKEN")
    github_repository = require_env("GITHUB_REPOSITORY")

    click.echo(f"Processing PR #{pr_number} in '{github_repository}'...")
    click.echo(f"Hardcoded allowed authors for automerge: {', '.join(AUTOMERGE_ALLOWED_AUTHORS)}")

    github_client = Github(github_token)
    repo = github_client.get_repo(github_repository)
    pr = repo.get_pull(pr_number)
    pr_author_login = pr.user.login

    click.echo(f"Pull Request #{pr_number} is authored by @{pr_author_login}")

    if pr_author_login not in AUTOMERGE_ALLOWED_AUTHORS:
        raise click.ClickException(f"Author @{pr_author_login} is NOT on the hardcoded allow list. Aborting automerge.")

    click.echo(f"Author @{pr_author_login} is on the allow list.")

    for pull_request_file in pr.get_files():
        if pull_request_file.status == "removed":
            raise click.ClickException(f"Pull Request #{pr_number} contains removed files. Aborting automerge.")
        if pull_request_file.filename not in AUTOMERGE_ALLOWED_FILES:
            raise click.ClickException(
                f"Pull Request #{pr_number} contains changes in the file '{pull_request_file.filename}' which is not allowed for automerge."
            )

    click.echo("Approving Pull Request...")
    pr.create_review(event="APPROVE")
    click.echo("Pull Request approved.")

    pr.enable_automerge(merge_method="SQUASH")
    click.echo("Pull Request will be automerged when build succeeds.")
