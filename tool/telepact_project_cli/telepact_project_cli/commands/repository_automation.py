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
from pathlib import Path

import click
from github import Github, GithubException

from .project_version import bump_version
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
MAIN_BRANCH = "main"
MERGE_ALLOWED_PERMISSIONS = {"admin", "maintain", "write"}
SUCCESSFUL_CHECK_STATES = {"success", "neutral", "skipped"}
PENDING_CHECK_STATES = {"pending", "queued", "in_progress", "requested", "waiting"}
REQUIREMENT_POLL_INTERVAL_SECONDS = 10
REQUIREMENT_POLL_ATTEMPTS = 90

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


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable is not set.")
    return value


def _run_git(args: list[str], *, capture_output: bool = False) -> str:
    completed = subprocess.run(
        ["git"] + args,
        check=True,
        stdout=subprocess.PIPE if capture_output else None,
        text=True,
    )
    return completed.stdout.strip() if capture_output else ""


def _get_modified_files(base_branch, head_sha):
    try:
        subprocess.run(["git", "fetch", "origin", base_branch], check=True)
        result = subprocess.run(["git", "diff", "--name-only", f"origin/{base_branch}", head_sha], check=True, stdout=subprocess.PIPE)
        files = result.stdout.decode("utf-8").strip()
        return files
    except subprocess.CalledProcessError as e:
        print(f"Error fetching or diffing: {e}")
        return ""


def _get_modified_project_labels(files):
    tags = set()
    for file in files.split():
        for directory, tag in PROJECT_LABEL_MAP.items():
            if file.startswith(directory):
                tags.add(tag)
    return tags


def _validate_commenter_can_merge(repo, commenter_login: str) -> None:
    try:
        permission = repo.get_collaborator_permission(commenter_login)
    except GithubException as exc:
        if exc.status == 404:
            raise click.ClickException(f"Commenter @{commenter_login} is not eligible to merge pull requests.") from exc
        raise

    if permission not in MERGE_ALLOWED_PERMISSIONS:
        raise click.ClickException(
            f"Commenter @{commenter_login} does not have merge permission (found: {permission})."
        )


def _validate_merge_pr_state(pr, github_repository: str) -> None:
    if pr.state != "open":
        raise click.ClickException(f"Pull request #{pr.number} is not open.")
    if pr.base.ref != MAIN_BRANCH:
        raise click.ClickException(f"Pull request #{pr.number} must target {MAIN_BRANCH}.")
    if pr.head.repo is None or pr.head.repo.full_name != github_repository:
        raise click.ClickException("Pull request head branch must live in this repository.")


def _wait_for_condition(description: str, predicate) -> object:
    for _ in range(REQUIREMENT_POLL_ATTEMPTS):
        value = predicate()
        if value is not None:
            return value
        time.sleep(REQUIREMENT_POLL_INTERVAL_SECONDS)
    raise click.ClickException(f"Timed out waiting for {description}.")


def _checkout_pr_branch(pr) -> str:
    branch_name = pr.head.ref
    _run_git(["fetch", "origin", MAIN_BRANCH, branch_name])
    _run_git(["checkout", "-B", branch_name, f"origin/{branch_name}"])
    return branch_name


def _branch_is_behind_main() -> bool:
    counts = _run_git(["rev-list", "--left-right", "--count", f"HEAD...origin/{MAIN_BRANCH}"], capture_output=True)
    _, behind_count = counts.split()
    return int(behind_count) > 0


def _wait_for_head_sha(repo, pr_number: int, expected_head_sha: str, *, allowed_previous_sha: str | None = None):
    observed_expected_head = False

    def _predicate():
        nonlocal observed_expected_head
        pr = repo.get_pull(pr_number)
        current_head_sha = pr.head.sha
        if current_head_sha == expected_head_sha:
            observed_expected_head = True
            return pr
        if current_head_sha == allowed_previous_sha and not observed_expected_head:
            return None
        raise click.ClickException(
            f"Pull request head changed unexpectedly while waiting for {expected_head_sha}: now {current_head_sha}."
        )

    return _wait_for_condition(f"pull request #{pr_number} head to become {expected_head_sha}", _predicate)


def _tidy_up_pull_request(repo, pr, branch_name: str):
    if pr.draft:
        pr.mark_ready_for_review()

        def _not_draft():
            refreshed_pr = repo.get_pull(pr.number)
            if refreshed_pr.draft:
                return None
            return refreshed_pr

        pr = _wait_for_condition(f"pull request #{pr.number} to leave draft state", _not_draft)

    if _branch_is_behind_main():
        previous_head_sha = pr.head.sha
        try:
            pr.update_branch(expected_head_sha=previous_head_sha)
        except GithubException as exc:
            raise click.ClickException(f"Failed to update pull request #{pr.number} with {MAIN_BRANCH}: {exc}") from exc

        def _head_changed():
            refreshed_pr = repo.get_pull(pr.number)
            if refreshed_pr.head.sha == previous_head_sha:
                return None
            return refreshed_pr

        pr = _wait_for_condition(f"pull request #{pr.number} branch update", _head_changed)
        _run_git(["fetch", "origin", MAIN_BRANCH, branch_name])
        _run_git(["reset", "--hard", f"origin/{branch_name}"])

    return pr


def _required_status_contexts(branch) -> set[str]:
    try:
        required_checks = branch.get_required_status_checks()
    except GithubException as exc:
        if exc.status == 404:
            return set()
        raise
    return set(required_checks.contexts)


def _collect_check_states(commit) -> dict[str, str]:
    states: dict[str, str] = {}

    for status in commit.get_statuses():
        states[status.context] = status.state

    for check_run in commit.get_check_runs():
        if check_run.status != "completed":
            states[check_run.name] = check_run.status
        else:
            states[check_run.name] = check_run.conclusion or "pending"

    return states


def _evaluate_context_states(states: dict[str, str], tracked_contexts: set[str]) -> tuple[list[str], list[str]]:
    pending: list[str] = []
    failed: list[str] = []

    for context in sorted(tracked_contexts):
        state = states.get(context)
        if state is None or state in PENDING_CHECK_STATES:
            pending.append(context)
        elif state not in SUCCESSFUL_CHECK_STATES:
            failed.append(f"{context}={state}")

    return pending, failed


def _wait_for_pr_requirements(repo, pr_number: int, expected_head_sha: str):
    branch = repo.get_branch(MAIN_BRANCH)
    required_contexts = _required_status_contexts(branch)

    def _predicate():
        pr = repo.get_pull(pr_number)
        _validate_merge_pr_state(pr, repo.full_name)
        if pr.head.sha != expected_head_sha:
            raise click.ClickException(
                f"Pull request #{pr_number} received new commits while waiting for checks: {pr.head.sha}."
            )
        if pr.draft:
            raise click.ClickException(f"Pull request #{pr_number} is still a draft.")

        commit = repo.get_commit(expected_head_sha)
        states = _collect_check_states(commit)
        tracked_contexts = required_contexts or set(states)
        pending_contexts, failed_contexts = _evaluate_context_states(states, tracked_contexts)

        if failed_contexts:
            raise click.ClickException(
                "Pull request requirements failed: " + ", ".join(failed_contexts)
            )
        if pending_contexts:
            return None
        if pr.mergeable is None or pr.mergeable_state == "unknown":
            return None
        if not pr.mergeable or pr.mergeable_state != "clean":
            raise click.ClickException(
                f"Pull request requirements are not satisfied: mergeable_state={pr.mergeable_state}."
            )
        return pr

    return _wait_for_condition(f"pull request #{pr_number} requirements", _predicate)


def _list_changed_paths_against_main() -> list[str]:
    output = _run_git(["diff", "--name-only", f"origin/{MAIN_BRANCH}...HEAD"], capture_output=True)
    return [line for line in output.splitlines() if line]


@click.command()
def github_labels() -> None:
    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number_str = os.getenv("PR_NUMBER")
    if not pr_number_str:
        click.echo("PR_NUMBER environment variable not set.", err=True)
        sys.exit(1)
    pr_number = int(pr_number_str)
    base_branch = os.getenv("BASE_BRANCH")
    head_sha = os.getenv("HEAD_SHA")

    files = _get_modified_files(base_branch, head_sha)
    print(f"Modified files: {files}")

    g = Github(token)
    repo = g.get_repo(repository)
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
    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")

    if not token or not repository:
        click.echo("GITHUB_TOKEN and GITHUB_REPOSITORY environment variables must be set.")
        return

    head_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()

    print(f"head_commit: {head_commit}")

    manifest_file = Path(".release/release-manifest.json")
    if manifest_file.exists():
        release_manifest = load_release_manifest(Path("."))
        version = release_manifest["version"]
        pr_number = int(release_manifest["pr_number"])
        release_targets = list(release_manifest.get("targets", []))
        click.echo("Loaded release metadata from .release/release-manifest.json")
    else:
        click.echo("No release manifest found.")
        return

    print(f"release_targets: {release_targets}")
    print(f"version: {version}")
    print(f"pr_number: {pr_number}")

    tag_name = version
    release_name = version

    g = Github(token)
    repo = g.get_repo(repository)
    pr = repo.get_pull(pr_number)

    if "go" in release_targets:
        go_tag_version = version if version.startswith("v") else f"v{version}"
        go_module_tag = f"lib/go/{go_tag_version}"
        try:
            existing_ref = repo.get_git_ref(f"tags/{go_module_tag}")
            existing_sha = existing_ref.object.sha
            if existing_sha != head_commit:
                raise RuntimeError(
                    f"Go module tag {go_module_tag} already exists at {existing_sha}, expected {head_commit}."
                )
            click.echo(f"Go module tag already exists: {go_module_tag}")
        except GithubException as e:
            if e.status != 404:
                raise
            repo.create_git_ref(ref=f"refs/tags/{go_module_tag}", sha=head_commit)
            click.echo(f"Created Go module tag: {go_module_tag}")

    pr_title = pr.title
    pr_url = pr.html_url
    released_projects = "".join(f"- {target}\n" for target in release_targets) if release_targets else "(None)"
    final_release_body = (
        f"## {pr_title} [(#{pr_number})]({pr_url})\n\n"
        f"### Released Projects\n"
        f"{released_projects}"
    ).strip()

    try:
        release = repo.create_git_release(
            tag=tag_name,
            name=release_name,
            message=final_release_body,
            draft=False,
            prerelease=True,
            target_commitish=head_commit,
        )
        click.echo(f"Release created: {release.html_url}")

        asset_count = 0
        for target in release_targets:
            asset_directories = RELEASE_TARGET_ASSET_DIRECTORY_MAP.get(target, [])
            for asset_directory in asset_directories:
                if os.path.exists(asset_directory):
                    for file_name in os.listdir(asset_directory):
                        if asset_count >= MAX_ASSETS:
                            click.echo("Maximum asset upload limit reached. Aborting.")
                            return
                        file_path = os.path.join(asset_directory, file_name)
                        if os.path.isfile(file_path):
                            with open(file_path, "rb") as asset_file:
                                release.upload_asset(
                                    path=file_path,
                                    name=file_name,
                                    label=f" [{target}]: {file_name}",
                                )
                                asset_count += 1
                                click.echo(f"Uploaded asset: {file_name} for target: {target}")
                else:
                    click.echo(f"Asset directory does not exist: {asset_directory} for target: {target}")

    except Exception as e:
        click.echo(f"Failed to create release or upload assets: {e}")


@click.command(name="publish-targets")
@click.option("--release-tag", default=None, help="Expected release tag/version for validation.")
@click.option("--release-body", default=None, help="Unused compatibility option; release targets come from the manifest.")
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path), help="Write key=value lines for GitHub Actions outputs.")
def publish_targets(release_tag: str | None, release_body: str | None, github_output: Path | None) -> None:
    outputs = resolve_publish_targets(
        Path("."),
        release_tag=release_tag,
        release_body=release_body,
    )

    lines = [f"{key}={'true' if value else 'false'}" for key, value in outputs.items()]
    if github_output is not None:
        github_output.parent.mkdir(parents=True, exist_ok=True)
        github_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        click.echo("\n".join(lines))


@click.command()
def automerge():
    pr_number_str = os.getenv("PR_NUMBER")
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")

    if not pr_number_str:
        raise Exception("PR_NUMBER environment variable is not set.")

    pr_number = int(pr_number_str)

    if not github_token:
        raise Exception("GITHUB_TOKEN environment variable is not set.")
    if not github_repository:
        raise Exception("GITHUB_REPOSITORY environment variable is not set (e.g., 'owner/repo').")

    print(f"Processing PR #{pr_number} in '{github_repository}'...")
    print(f"Hardcoded allowed authors for automerge: {', '.join(AUTOMERGE_ALLOWED_AUTHORS)}")

    g = Github(github_token)
    repo_obj = g.get_repo(github_repository)
    pr = repo_obj.get_pull(pr_number)

    pr_author_login = pr.user.login
    print(f"Pull Request #{pr_number} is authored by @{pr_author_login}")

    if pr_author_login not in AUTOMERGE_ALLOWED_AUTHORS:
        raise Exception(f"Author @{pr_author_login} is NOT on the hardcoded allow list. Aborting automerge.")
    else:
        print(f"Author @{pr_author_login} is on the allow list.")

    for f in pr.get_files():
        if f.status == "removed":
            raise Exception(f"Pull Request #{pr_number} contains removed files. Aborting automerge.")
        if f.filename not in AUTOMERGE_ALLOWED_FILES:
            raise Exception(f"Pull Request #{pr_number} contains changes in the file '{f.filename}' which is not allowed for automerge.")

    print("Approving Pull Request...")
    pr.create_review(event="APPROVE")
    print("Pull Request approved.")

    pr.enable_automerge(merge_method="SQUASH")
    print("Pull Request will be automerged when build succeeds.")


@click.command(name="merge-pr")
def merge_pr() -> None:
    pr_number = int(_require_env("PR_NUMBER"))
    github_token = _require_env("GITHUB_TOKEN")
    github_repository = _require_env("GITHUB_REPOSITORY")
    commenter_login = _require_env("COMMENTER_LOGIN")

    github_client = Github(github_token)
    repo = github_client.get_repo(github_repository)
    _validate_commenter_can_merge(repo, commenter_login)

    pr = repo.get_pull(pr_number)
    _validate_merge_pr_state(pr, github_repository)

    branch_name = _checkout_pr_branch(pr)
    pr = _tidy_up_pull_request(repo, pr, branch_name)
    pr = _wait_for_pr_requirements(repo, pr_number, pr.head.sha)

    changed_paths = _list_changed_paths_against_main()
    bump_version(pr_number, changed_paths)
    bumped_head_sha = _run_git(["rev-parse", "HEAD"], capture_output=True)
    _run_git(["push", "origin", f"HEAD:{branch_name}"])

    pr = _wait_for_head_sha(repo, pr_number, bumped_head_sha, allowed_previous_sha=pr.head.sha)
    pr = _wait_for_pr_requirements(repo, pr_number, pr.head.sha)

    merge_status = pr.merge(merge_method="squash", sha=pr.head.sha)
    if not merge_status.merged:
        raise click.ClickException(f"Failed to merge pull request #{pr_number}: {merge_status.message}")

    click.echo(f"Pull request #{pr_number} merged.")
