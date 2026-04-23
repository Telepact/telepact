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
import time
from pathlib import Path

import click
from github import Github, GithubException
from github.PullRequest import PullRequest

from .project_version import create_version_bump_commit
from ..release_plan import load_release_manifest, resolve_publish_targets

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
MERGE_READY_LABEL = "Merge Ready"
WAIT_TIMEOUT_SECONDS = 20 * 60  # 20 minutes
WAIT_INTERVAL_SECONDS = 10
MERGE_ALLOWED_PERMISSIONS = {"write", "maintain", "admin"}
PENDING_MERGEABLE_STATES = {"unknown"}
PENDING_CHECK_STATES = {"expected", "pending", "queued", "requested", "waiting", "in_progress"}
FAILED_COMBINED_STATUS_STATES = {"error", "failure"}
# GitHub check runs treat "neutral" and "skipped" as completed non-failures, while
# interrupted or incomplete conclusions such as "cancelled", "timed_out",
# "stale", and "action_required" should stop merge-pr immediately.
FAILED_CHECK_RUN_CONCLUSIONS = {"action_required", "cancelled", "failure", "startup_failure", "stale", "timed_out"}
SUCCESSFUL_CHECK_RUN_CONCLUSIONS = {"neutral", "skipped", "success"}

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


def _git(*args: str, capture_output: bool = False) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture_output else None,
    )
    return result.stdout.strip() if capture_output else ""


def _current_head_sha() -> str:
    return _git("rev-parse", "HEAD", capture_output=True)


def _write_github_output(name: str, value: str) -> None:
    github_output = os.getenv("GITHUB_OUTPUT")
    if not github_output:
        return
    with open(github_output, "a", encoding="utf-8") as output_file:
        output_file.write(f"{name}={value}\n")


def _checkout_pr_branch(head_ref: str) -> None:
    remote_ref = f"refs/remotes/origin/{head_ref}"
    _git("fetch", "origin", f"refs/heads/{head_ref}:{remote_ref}")
    _git("checkout", "-B", head_ref, remote_ref)


def _push_current_branch(head_ref: str) -> None:
    _git("push", "origin", f"HEAD:{head_ref}")


def _wait_for_pr_stable(repo, pr_number: int, expected_head_sha: str) -> PullRequest:
    deadline = time.monotonic() + WAIT_TIMEOUT_SECONDS
    while True:
        pr = repo.get_pull(pr_number)
        if pr.head.sha != expected_head_sha:
            raise RuntimeError(
                f"Pull request head changed unexpectedly from {expected_head_sha} to {pr.head.sha}."
            )
        mergeable_state = pr.mergeable_state or ""
        if pr.mergeable is not None and mergeable_state not in PENDING_MERGEABLE_STATES:
            return pr
        if time.monotonic() >= deadline:
            raise TimeoutError("Timed out waiting for pull request mergeability to stabilize.")
        time.sleep(WAIT_INTERVAL_SECONDS)


def _wait_for_pr_head_update(repo, pr_number: int, previous_head_sha: str) -> PullRequest:
    deadline = time.monotonic() + WAIT_TIMEOUT_SECONDS
    while True:
        pr = repo.get_pull(pr_number)
        mergeable_state = pr.mergeable_state or ""
        if pr.head.sha != previous_head_sha and pr.mergeable is not None and mergeable_state not in PENDING_MERGEABLE_STATES:
            return pr
        if time.monotonic() >= deadline:
            raise TimeoutError("Timed out waiting for pull request branch update to complete.")
        time.sleep(WAIT_INTERVAL_SECONDS)


def _wait_for_expected_head(repo, pr_number: int, previous_head_sha: str, expected_head_sha: str) -> PullRequest:
    deadline = time.monotonic() + WAIT_TIMEOUT_SECONDS
    while True:
        pr = repo.get_pull(pr_number)
        if pr.head.sha == expected_head_sha:
            return pr
        if pr.head.sha != previous_head_sha:
            raise RuntimeError(
                f"Pull request head changed unexpectedly from {previous_head_sha} to {pr.head.sha}; expected {expected_head_sha}."
            )
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for pull request head {expected_head_sha}.")
        time.sleep(WAIT_INTERVAL_SECONDS)


def _combined_status_state(pr: PullRequest) -> str:
    combined_status = pr.base.repo.get_commit(pr.head.sha).get_combined_status()
    return (combined_status.state or "").lower()


def _check_runs_state(pr: PullRequest) -> str | None:
    check_runs = list(pr.base.repo.get_commit(pr.head.sha).get_check_runs())
    if not check_runs:
        return None

    pending = False
    for check_run in check_runs:
        status = (check_run.status or "").lower()
        conclusion = (check_run.conclusion or "").lower()
        if status != "completed":
            pending = True
            continue
        if not conclusion:
            return "error_no_conclusion"
        if conclusion in FAILED_CHECK_RUN_CONCLUSIONS:
            return conclusion
        if conclusion not in SUCCESSFUL_CHECK_RUN_CONCLUSIONS:
            return f"unknown_conclusion:{conclusion}"

    if pending:
        return "pending"
    return "success"


def _pull_request_ci_state(pr: PullRequest) -> str:
    check_runs_state = _check_runs_state(pr)
    if check_runs_state is not None:
        return check_runs_state
    return _combined_status_state(pr)


def _verify_pull_request_ci(repo, pr_number: int, expected_head_sha: str) -> PullRequest:
    deadline = time.monotonic() + WAIT_TIMEOUT_SECONDS
    while True:
        pr = _wait_for_pr_stable(repo, pr_number, expected_head_sha)
        ci_state = _pull_request_ci_state(pr)
        if ci_state == "success":
            return pr
        if ci_state in FAILED_COMBINED_STATUS_STATES or ci_state in FAILED_CHECK_RUN_CONCLUSIONS:
            raise RuntimeError(f"Pull request #{pr.number} CI failed with state {ci_state!r}.")
        if ci_state not in PENDING_CHECK_STATES:
            raise RuntimeError(f"Pull request #{pr.number} has unexpected CI state {ci_state!r}.")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for pull request #{pr.number} CI to complete.")
        time.sleep(WAIT_INTERVAL_SECONDS)


def _validate_merge_request(pr, is_admin: bool) -> None:
    if pr.state != "open":
        raise RuntimeError(f"Pull request #{pr.number} is not open.")
    if pr.base.ref != MAIN_BRANCH:
        raise RuntimeError(f"Pull request #{pr.number} must target {MAIN_BRANCH}.")
    if pr.head.repo is None or pr.head.repo.full_name != pr.base.repo.full_name:
        raise RuntimeError("Cross-repository pull requests are not supported by merge-pr.")

    combined_status_state = _pull_request_ci_state(pr)
    mergeable_state = pr.mergeable_state or ""
    mergeable = pr.mergeable

    if mergeable_state == "blocked" and combined_status_state == "success" and not is_admin:
        raise RuntimeError(f"Pull request #{pr.number} is blocked after CI succeeded because required approving reviews are missing.")

    if mergeable is None:
        raise RuntimeError(f"Pull request #{pr.number} mergeability is still being calculated.")

    if mergeable is False:
        if mergeable_state in {"behind", "draft"}:
            return
        raise RuntimeError(f"Pull request #{pr.number} is not mergeable (state={pr.mergeable_state}).")


def _pull_request_changed_paths(pr: PullRequest) -> list[str]:
    return sorted({file.filename for file in pr.get_files() if file.filename})


def _require_merge_permission(repo, commenter_login: str) -> str:
    if not repo.has_in_collaborators(commenter_login):
        raise click.ClickException(f"User @{commenter_login} is not a repository collaborator.")

    commenter_permission = repo.get_collaborator_permission(commenter_login)
    if commenter_permission not in MERGE_ALLOWED_PERMISSIONS:
        raise RuntimeError(f"User @{commenter_login} does not have permission to merge pull requests.")

    return commenter_permission


def _is_merge_ready_pull_request(pr: PullRequest) -> bool:
    return any(label.name == MERGE_READY_LABEL for label in pr.get_labels())


def _list_open_merge_ready_pull_requests(repo) -> list[PullRequest]:
    return [
        pr
        for pr in repo.get_pulls(state="open", sort="created", direction="asc", base=MAIN_BRANCH)
        if _is_merge_ready_pull_request(pr)
    ]


def _process_merge_pull_request(repo, pr_number: int, is_admin: bool) -> None:
    pr = repo.get_pull(pr_number)
    expected_head_sha = pr.head.sha
    pr = _wait_for_pr_stable(repo, pr_number, expected_head_sha)
    _validate_merge_request(pr, is_admin)
    changed_paths = _pull_request_changed_paths(pr)

    if pr.draft:
        click.echo(f"Marking pull request #{pr.number} ready for review.")
        pr.mark_ready_for_review()
        pr = _wait_for_pr_stable(repo, pr_number, expected_head_sha)

    if pr.mergeable_state == "behind":
        click.echo(f"Updating pull request #{pr.number} with main.")
        previous_head_sha = expected_head_sha
        pr.update_branch(expected_head_sha=expected_head_sha)
        pr = _wait_for_pr_head_update(repo, pr_number, previous_head_sha)
        expected_head_sha = pr.head.sha

    _checkout_pr_branch(pr.head.ref)
    _verify_pull_request_ci(repo, pr_number, expected_head_sha)

    click.echo(f"Bumping version on branch {pr.head.ref}.")
    create_version_bump_commit(pr_number, changed_paths=changed_paths)
    bumped_head_sha = _current_head_sha()
    _push_current_branch(pr.head.ref)

    pr = _wait_for_expected_head(repo, pr_number, expected_head_sha, bumped_head_sha)
    expected_head_sha = pr.head.sha
    _validate_merge_request(pr, is_admin)

    merge_result = pr.merge(merge_method="squash", sha=expected_head_sha)
    if not merge_result.merged:
        raise RuntimeError(f"Failed to merge pull request #{pr.number}: {merge_result.message}")

    click.echo(f"Merged pull request #{pr.number} with squash.")


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


@click.command(name="merge-pr")
def merge_pr() -> None:
    github_token = _require_env("GITHUB_TOKEN")
    github_repository = _require_env("GITHUB_REPOSITORY")

    repo = Github(github_token).get_repo(github_repository)
    while True:
        merge_ready_pull_requests = _list_open_merge_ready_pull_requests(repo)
        if not merge_ready_pull_requests:
            click.echo(f"No open pull requests labeled '{MERGE_READY_LABEL}'.")
            return

        pr = merge_ready_pull_requests[0]
        click.echo(f"Processing pull request #{pr.number}.")
        _process_merge_pull_request(repo, pr.number, is_admin=False)


@click.command(name="mark-pr-merge-ready")
def mark_pr_merge_ready() -> None:
    github_token = _require_env("GITHUB_TOKEN")
    github_repository = _require_env("GITHUB_REPOSITORY")
    commenter_login = _require_env("COMMENTER_LOGIN")
    pr_number = int(_require_env("PR_NUMBER"))

    repo = Github(github_token).get_repo(github_repository)
    commenter_permission = _require_merge_permission(repo, commenter_login)

    pr = repo.get_pull(pr_number)
    if pr.state != "open":
        raise RuntimeError(f"Pull request #{pr.number} is not open.")

    if not _is_merge_ready_pull_request(pr):
        pr.add_to_labels(MERGE_READY_LABEL)
        click.echo(f"Added '{MERGE_READY_LABEL}' label to pull request #{pr.number}.")
    else:
        click.echo(f"Pull request #{pr.number} already has the '{MERGE_READY_LABEL}' label.")

    merge_ready_count = len(_list_open_merge_ready_pull_requests(repo))
    skip_merge_loop = merge_ready_count > 1
    _write_github_output("skip_merge_loop", "true" if skip_merge_loop else "false")
    _write_github_output("merge_ready_count", str(merge_ready_count))
    _write_github_output("commenter_permission", commenter_permission)
    click.echo(f"Open pull requests labeled '{MERGE_READY_LABEL}': {merge_ready_count}.")
    if skip_merge_loop:
        click.echo("Skipping merge loop start because another merge-ready pull request is already queued.")


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
