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

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click
from github import Github, GithubException

from ..github_utils import github_rest_request, require_env, write_github_outputs
from ..release_plan import load_release_manifest, resolve_publish_targets

PROJECT_LABEL_MAP = {
    "lib/java": "java",
    "lib/py": "py",
    "lib/ts": "ts",
    "lib/go": "go",
    "bind/dart": "dart",
    "sdk/cli": "cli",
    "sdk/console": "console",
    "sdk/prettier": "prettier",
}

RELEASE_TARGET_ASSET_DIRECTORY_MAP = {
    "java": ["lib/java/target/central-publishing"],
    "py": ["lib/py/dist"],
    "ts": ["lib/ts/dist-tgz"],
    "dart": ["bind/dart/dist"],
    "cli": ["sdk/cli/dist", "sdk/cli/dist-docker"],
    "console": ["sdk/console/dist-tgz", "sdk/console/dist-docker"],
    "prettier": ["sdk/prettier/dist-tgz"],
}

MAX_ASSETS = 10
AUTOMERGE_ALLOWED_AUTHORS = ["dependabot[bot]"]
AUTOMERGE_ALLOWED_FILES = [
    "bind/dart/package-lock.json",
    "bind/dart/package.json",
    "bind/dart/pubspec.lock",
    "bind/dart/pubspec.yaml",
    "lib/java/pom.xml",
    "lib/py/uv.lock",
    "lib/py/pyproject.toml",
    "lib/ts/package-lock.json",
    "lib/ts/package.json",
    "package-lock.json",
    "package.json",
    "sdk/cli/uv.lock",
    "sdk/cli/pyproject.toml",
    "sdk/console/package-lock.json",
    "sdk/console/package.json",
    "sdk/prettier/package-lock.json",
    "sdk/prettier/package.json",
    "test/console-self-hosted/package.json",
    "test/lib/java/pom.xml",
    "test/lib/py/pyproject.toml",
    "test/lib/ts/package.json",
    "test/runner/uv.lock",
    "test/runner/pyproject.toml",
    "tool/telepact_project_cli/uv.lock",
    "tool/telepact_project_cli/pyproject.toml",
]

ALLOWED_MERGE_PERMISSIONS = {"admin", "maintain", "write"}
PULL_REQUEST_WORKFLOW_NAME = "PR"
DEFAULT_POLL_INTERVAL_SECONDS = 10
DEFAULT_TIMEOUT_SECONDS = 30 * 60


@dataclass(frozen=True)
class PullRequestState:
    number: int
    title: str
    state: str
    merged: bool
    draft: bool
    base_ref: str
    head_ref: str
    head_sha: str
    mergeable: bool | None
    mergeable_state: str | None


def _parse_pr_number() -> int:
    return int(require_env("PR_NUMBER"))


def _github_context() -> tuple[str, str]:
    return require_env("GITHUB_TOKEN"), require_env("GITHUB_REPOSITORY")


def _get_modified_files(base_branch: str, head_sha: str) -> str:
    try:
        subprocess.run(["git", "fetch", "origin", base_branch], check=True)
        result = subprocess.run(["git", "diff", "--name-only", f"origin/{base_branch}", head_sha], check=True, stdout=subprocess.PIPE)
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError as exc:
        print(f"Error fetching or diffing: {exc}")
        return ""


def _get_modified_project_labels(files: str) -> set[str]:
    tags = set()
    for file in files.split():
        for directory, tag in PROJECT_LABEL_MAP.items():
            if file.startswith(directory):
                tags.add(tag)
    return tags


def _load_pull_request_state(token: str, repository: str, pr_number: int) -> PullRequestState:
    _, data = github_rest_request(token, "GET", f"/repos/{repository}/pulls/{pr_number}")
    return PullRequestState(
        number=data["number"],
        title=data["title"],
        state=data["state"],
        merged=bool(data["merged"]),
        draft=bool(data["draft"]),
        base_ref=data["base"]["ref"],
        head_ref=data["head"]["ref"],
        head_sha=data["head"]["sha"],
        mergeable=data.get("mergeable"),
        mergeable_state=data.get("mergeable_state"),
    )


def _wait_for_stable_pull_request_state(
    token: str,
    repository: str,
    pr_number: int,
    poll_interval: int,
    timeout: int,
) -> PullRequestState:
    deadline = time.monotonic() + timeout
    while True:
        state = _load_pull_request_state(token, repository, pr_number)
        if state.mergeable is not None and state.mergeable_state not in {None, "unknown"}:
            return state
        if time.monotonic() >= deadline:
            raise click.ClickException(f"Timed out waiting for Pull Request #{pr_number} mergeability to stabilize.")
        time.sleep(poll_interval)


def _ensure_open_pr_on_main(pr_state: PullRequestState) -> None:
    if pr_state.state != "open" or pr_state.merged:
        raise click.ClickException(f"Pull Request #{pr_state.number} is not open.")
    if pr_state.base_ref != "main":
        raise click.ClickException(f"Pull Request #{pr_state.number} must target main, found {pr_state.base_ref!r}.")


def _ensure_expected_head(pr_state: PullRequestState, expected_head_sha: str | None) -> None:
    if expected_head_sha and pr_state.head_sha != expected_head_sha:
        raise click.ClickException(
            f"Pull Request #{pr_state.number} head changed unexpectedly: expected {expected_head_sha}, found {pr_state.head_sha}."
        )


def _load_collaborator_permission(token: str, repository: str, login: str) -> str:
    _, data = github_rest_request(token, "GET", f"/repos/{repository}/collaborators/{login}/permission")
    permission = data.get("permission")
    if not isinstance(permission, str) or not permission:
        raise click.ClickException(f"Unable to determine repository permission for @{login}.")
    return permission


def _pr_is_behind_base(token: str, repository: str, pr_state: PullRequestState) -> bool:
    _, data = github_rest_request(token, "GET", f"/repos/{repository}/compare/{pr_state.base_ref}...{pr_state.head_sha}")
    return int(data.get("behind_by", 0)) > 0


def _load_review_states(token: str, repository: str, pr_number: int) -> dict[str, str]:
    _, reviews = github_rest_request(token, "GET", f"/repos/{repository}/pulls/{pr_number}/reviews?per_page=100")
    latest_by_user: dict[str, tuple[str, str]] = {}
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login")
        state = review.get("state")
        submitted_at = review.get("submitted_at") or ""
        if not login or not state:
            continue
        previous = latest_by_user.get(login)
        if previous is None or submitted_at >= previous[0]:
            latest_by_user[login] = (submitted_at, state)
    return {login: state for login, (_, state) in latest_by_user.items()}


def _verify_review_requirements(token: str, repository: str, pr_number: int) -> None:
    latest_states = _load_review_states(token, repository, pr_number)
    if any(state == "CHANGES_REQUESTED" for state in latest_states.values()):
        raise click.ClickException(f"Pull Request #{pr_number} has requested changes.")
    if not any(state == "APPROVED" for state in latest_states.values()):
        raise click.ClickException(f"Pull Request #{pr_number} does not have an approval.")


def _latest_pr_workflow_run(token: str, repository: str, head_sha: str) -> dict[str, Any] | None:
    _, data = github_rest_request(
        token,
        "GET",
        f"/repos/{repository}/actions/runs?event=pull_request&head_sha={head_sha}&per_page=100",
    )
    runs = [
        run
        for run in data.get("workflow_runs", [])
        if run.get("name") == PULL_REQUEST_WORKFLOW_NAME and run.get("head_sha") == head_sha
    ]
    if not runs:
        return None
    runs.sort(key=lambda run: (run.get("created_at") or "", run.get("id") or 0), reverse=True)
    return runs[0]


def _verify_build_requirements(
    token: str,
    repository: str,
    pr_number: int,
    expected_head_sha: str,
    poll_interval: int,
    timeout: int,
) -> PullRequestState:
    deadline = time.monotonic() + timeout
    while True:
        pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)
        _ensure_open_pr_on_main(pr_state)
        _ensure_expected_head(pr_state, expected_head_sha)

        if pr_state.draft:
            raise click.ClickException(f"Pull Request #{pr_number} is still a draft.")
        if pr_state.mergeable is False or pr_state.mergeable_state == "dirty":
            raise click.ClickException(f"Pull Request #{pr_number} is not mergeable.")
        if _pr_is_behind_base(token, repository, pr_state):
            raise click.ClickException(f"Pull Request #{pr_number} is behind main.")

        _verify_review_requirements(token, repository, pr_number)

        workflow_run = _latest_pr_workflow_run(token, repository, expected_head_sha)
        if workflow_run is None or workflow_run.get("status") != "completed":
            if time.monotonic() >= deadline:
                raise click.ClickException(f"Timed out waiting for Pull Request #{pr_number} build completion.")
            time.sleep(poll_interval)
            continue

        if workflow_run.get("conclusion") != "success":
            raise click.ClickException(
                f"Pull Request #{pr_number} build did not succeed (conclusion={workflow_run.get('conclusion')!r})."
            )

        refreshed = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)
        _ensure_expected_head(refreshed, expected_head_sha)
        if refreshed.mergeable is False or refreshed.mergeable_state in {"behind", "blocked", "dirty", "draft"}:
            raise click.ClickException(
                f"Pull Request #{pr_number} is not ready to merge (mergeable_state={refreshed.mergeable_state!r})."
            )
        return refreshed


@click.command()
def github_labels() -> None:
    token, repository = _github_context()
    pr_number = _parse_pr_number()
    base_branch = require_env("BASE_BRANCH")
    head_sha = require_env("HEAD_SHA")

    files = _get_modified_files(base_branch, head_sha)
    print(f"Modified files: {files}")

    repo = Github(token).get_repo(repository)
    pr = repo.get_pull(pr_number)

    current_labels = {label.name for label in pr.get_labels()}
    new_labels = _get_modified_project_labels(files)

    print(f"Labels to be added: {new_labels}")

    added_labels = []
    removed_labels = []

    for label in new_labels:
        if label not in current_labels:
            pr.add_to_labels(label)
            added_labels.append(label)

    for label in current_labels:
        if label not in new_labels and label in PROJECT_LABEL_MAP.values():
            pr.remove_from_labels(label)
            removed_labels.append(label)

    print(
        f"Summary:\n  Added tags: {', '.join(added_labels) if added_labels else 'None'}\n  Removed tags: {', '.join(removed_labels) if removed_labels else 'None'}"
    )


@click.command()
def release() -> None:
    token, repository = _github_context()

    manifest_file = Path(".release/release-manifest.json")
    if not manifest_file.exists():
        raise click.ClickException("Release manifest not found at .release/release-manifest.json")

    release_manifest = load_release_manifest(Path("."))
    version = release_manifest["version"]
    pr_number = int(release_manifest["pr_number"])
    release_targets = list(release_manifest.get("targets", []))
    click.echo("Loaded release metadata from .release/release-manifest.json")

    head_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()

    print(f"release_targets: {release_targets}")
    print(f"version: {version}")
    print(f"pr_number: {pr_number}")

    repo = Github(token).get_repo(repository)
    pr = repo.get_pull(pr_number)

    if "go" in release_targets:
        go_tag_version = version if version.startswith("v") else f"v{version}"
        go_module_tag = f"lib/go/{go_tag_version}"
        try:
            existing_ref = repo.get_git_ref(f"tags/{go_module_tag}")
            existing_sha = existing_ref.object.sha
            if existing_sha != head_commit:
                raise RuntimeError(f"Go module tag {go_module_tag} already exists at {existing_sha}, expected {head_commit}.")
            click.echo(f"Go module tag already exists: {go_module_tag}")
        except GithubException as exc:
            if exc.status != 404:
                raise
            repo.create_git_ref(ref=f"refs/tags/{go_module_tag}", sha=head_commit)
            click.echo(f"Created Go module tag: {go_module_tag}")

    released_projects = "".join(f"- {target}\n" for target in release_targets) if release_targets else "(None)"
    final_release_body = (
        f"## {pr.title} [(#{pr_number})]({pr.html_url})\n\n"
        f"### Released Projects\n"
        f"{released_projects}"
    ).strip()

    try:
        release_obj = repo.create_git_release(
            tag=version,
            name=version,
            message=final_release_body,
            draft=False,
            prerelease=True,
            target_commitish=head_commit,
        )
        click.echo(f"Release created: {release_obj.html_url}")

        asset_count = 0
        for target in release_targets:
            for asset_directory in RELEASE_TARGET_ASSET_DIRECTORY_MAP.get(target, []):
                if not os.path.exists(asset_directory):
                    click.echo(f"Asset directory does not exist: {asset_directory} for target: {target}")
                    continue
                for file_name in os.listdir(asset_directory):
                    if asset_count >= MAX_ASSETS:
                        click.echo("Maximum asset upload limit reached. Aborting.")
                        return
                    file_path = os.path.join(asset_directory, file_name)
                    if os.path.isfile(file_path):
                        release_obj.upload_asset(path=file_path, name=file_name, label=f" [{target}]: {file_name}")
                        asset_count += 1
                        click.echo(f"Uploaded asset: {file_name} for target: {target}")
    except Exception as exc:
        click.echo(f"Failed to create release or upload assets: {exc}")


@click.command(name="publish-targets")
@click.option("--release-tag", default=None, help="Expected release tag/version for validation.")
@click.option("--release-body", default=None, help="Unused legacy option.")
@click.option(
    "--github-output",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write key=value lines for GitHub Actions outputs.",
)
def publish_targets(release_tag: str | None, release_body: str | None, github_output: Path | None) -> None:
    del release_body
    outputs = resolve_publish_targets(Path("."), release_tag=release_tag)
    lines = [f"{key}={'true' if value else 'false'}" for key, value in outputs.items()]
    if github_output is not None:
        github_output.parent.mkdir(parents=True, exist_ok=True)
        github_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        click.echo("\n".join(lines))


@click.command(name="verify-merge-conditions")
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path))
@click.option("--poll-interval", default=DEFAULT_POLL_INTERVAL_SECONDS, show_default=True)
@click.option("--timeout", default=DEFAULT_TIMEOUT_SECONDS, show_default=True)
def verify_merge_conditions(github_output: Path | None, poll_interval: int, timeout: int) -> None:
    token, repository = _github_context()
    pr_number = _parse_pr_number()
    commenter_login = require_env("COMMENTER_LOGIN")

    permission = _load_collaborator_permission(token, repository, commenter_login)
    if permission not in ALLOWED_MERGE_PERMISSIONS:
        raise click.ClickException(
            f"User @{commenter_login} does not have merge permission (found {permission!r})."
        )

    pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)
    _ensure_open_pr_on_main(pr_state)

    write_github_outputs(
        github_output,
        {
            "head_sha": pr_state.head_sha,
            "head_ref": pr_state.head_ref,
            "base_ref": pr_state.base_ref,
        },
    )


@click.command(name="tidy-pr")
@click.option("--expected-head-sha", default=None)
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path))
@click.option("--poll-interval", default=DEFAULT_POLL_INTERVAL_SECONDS, show_default=True)
@click.option("--timeout", default=DEFAULT_TIMEOUT_SECONDS, show_default=True)
def tidy_pr(expected_head_sha: str | None, github_output: Path | None, poll_interval: int, timeout: int) -> None:
    token, repository = _github_context()
    pr_number = _parse_pr_number()

    pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)
    _ensure_open_pr_on_main(pr_state)
    _ensure_expected_head(pr_state, expected_head_sha)

    if pr_state.draft:
        github_rest_request(
            token,
            "POST",
            f"/repos/{repository}/pulls/{pr_number}/ready_for_review",
            expected_statuses=(200,),
        )
        pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)

    if _pr_is_behind_base(token, repository, pr_state):
        original_head_sha = pr_state.head_sha
        github_rest_request(
            token,
            "PUT",
            f"/repos/{repository}/pulls/{pr_number}/update-branch",
            payload={"expected_head_sha": original_head_sha},
            expected_statuses=(202,),
        )

        deadline = time.monotonic() + timeout
        while True:
            pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)
            if pr_state.head_sha != original_head_sha and not _pr_is_behind_base(token, repository, pr_state):
                break
            if time.monotonic() >= deadline:
                raise click.ClickException(f"Timed out updating Pull Request #{pr_number} with main.")
            time.sleep(poll_interval)

    write_github_outputs(
        github_output,
        {
            "head_sha": pr_state.head_sha,
            "head_ref": pr_state.head_ref,
            "base_ref": pr_state.base_ref,
        },
    )


@click.command(name="verify-pr-requirements")
@click.option("--expected-head-sha", default=None)
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path))
@click.option("--poll-interval", default=DEFAULT_POLL_INTERVAL_SECONDS, show_default=True)
@click.option("--timeout", default=DEFAULT_TIMEOUT_SECONDS, show_default=True)
def verify_pr_requirements(
    expected_head_sha: str | None,
    github_output: Path | None,
    poll_interval: int,
    timeout: int,
) -> None:
    token, repository = _github_context()
    pr_number = _parse_pr_number()
    pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, poll_interval, timeout)
    _ensure_open_pr_on_main(pr_state)
    locked_head_sha = expected_head_sha or pr_state.head_sha

    verified_state = _verify_build_requirements(
        token,
        repository,
        pr_number,
        locked_head_sha,
        poll_interval,
        timeout,
    )

    write_github_outputs(
        github_output,
        {
            "head_sha": verified_state.head_sha,
            "head_ref": verified_state.head_ref,
            "base_ref": verified_state.base_ref,
        },
    )


@click.command(name="merge-pr")
@click.option("--expected-head-sha", required=True)
def merge_pr(expected_head_sha: str) -> None:
    token, repository = _github_context()
    pr_number = _parse_pr_number()
    pr_state = _wait_for_stable_pull_request_state(token, repository, pr_number, DEFAULT_POLL_INTERVAL_SECONDS, DEFAULT_TIMEOUT_SECONDS)
    _ensure_open_pr_on_main(pr_state)
    _ensure_expected_head(pr_state, expected_head_sha)
    if pr_state.draft:
        raise click.ClickException(f"Pull Request #{pr_number} is still a draft.")
    if _pr_is_behind_base(token, repository, pr_state):
        raise click.ClickException(f"Pull Request #{pr_number} is behind main.")

    github_rest_request(
        token,
        "PUT",
        f"/repos/{repository}/pulls/{pr_number}/merge",
        payload={"sha": expected_head_sha, "merge_method": "squash"},
        expected_statuses=(200,),
    )


@click.command()
def automerge() -> None:
    pr_number = _parse_pr_number()
    github_token, github_repository = _github_context()

    print(f"Processing PR #{pr_number} in '{github_repository}'...")
    print(f"Hardcoded allowed authors for automerge: {', '.join(AUTOMERGE_ALLOWED_AUTHORS)}")

    repo_obj = Github(github_token).get_repo(github_repository)
    pr = repo_obj.get_pull(pr_number)

    pr_author_login = pr.user.login
    print(f"Pull Request #{pr_number} is authored by @{pr_author_login}")

    if pr_author_login not in AUTOMERGE_ALLOWED_AUTHORS:
        raise Exception(f"Author @{pr_author_login} is NOT on the hardcoded allow list. Aborting automerge.")
    print(f"Author @{pr_author_login} is on the allow list.")

    for file in pr.get_files():
        if file.status == "removed":
            raise Exception(f"Pull Request #{pr_number} contains removed files. Aborting automerge.")
        if file.filename not in AUTOMERGE_ALLOWED_FILES:
            raise Exception(
                f"Pull Request #{pr_number} contains changes in the file '{file.filename}' which is not allowed for automerge."
            )

    print("Approving Pull Request...")
    pr.create_review(event="APPROVE")
    print("Pull Request approved.")

    pr.enable_automerge(merge_method="SQUASH")
    print("Pull Request will be automerged when build succeeds.")
