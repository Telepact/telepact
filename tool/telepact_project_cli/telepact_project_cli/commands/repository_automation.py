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

MERGE_ALLOWED_PERMISSIONS = {"admin", "maintain", "write"}
SUCCESSFUL_CHECK_CONCLUSIONS = {"success", "neutral", "skipped"}
PENDING_CHECK_STATUSES = {"in_progress", "pending", "queued", "requested", "waiting"}
PENDING_MERGEABLE_STATES = {"unknown"}
READY_CHECK_POLL_INTERVAL_SECONDS = 10
READY_CHECK_MAX_POLLS = 90
HEAD_UPDATE_MAX_POLLS = 30
GIT_USER_NAME = "telepact-notary[bot]"
GIT_USER_EMAIL = "telepact-notary[bot]@users.noreply.github.com"


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


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable is not set.")
    return value


def _run_git(*args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def _configure_git_identity() -> None:
    _run_git("config", "user.name", GIT_USER_NAME)
    _run_git("config", "user.email", GIT_USER_EMAIL)


def _validate_merge_commenter(repo, commenter_login: str) -> tuple[str, str]:
    if not repo.has_in_collaborators(commenter_login):
        raise click.ClickException(f"Commenter @{commenter_login} is not a repository collaborator.")

    permission = repo.get_collaborator_permission(commenter_login)
    if permission not in MERGE_ALLOWED_PERMISSIONS:
        raise click.ClickException(
            f"Commenter @{commenter_login} has repository permission {permission!r}, which cannot merge pull requests."
        )

    role_name = repo.get_collaborator_role_name(commenter_login)
    click.echo(f"Commenter @{commenter_login} is eligible to merge (permission={permission}, role={role_name}).")
    return permission, role_name


def _validate_pull_request_state(pr, repository_full_name: str) -> None:
    if pr.state != "open":
        raise click.ClickException(f"Pull request #{pr.number} is not open.")
    if pr.base.ref != "main":
        raise click.ClickException(f"Pull request #{pr.number} must target main, not {pr.base.ref!r}.")
    if pr.head.repo is None or pr.head.repo.full_name != repository_full_name:
        raise click.ClickException(
            f"Pull request #{pr.number} must use a branch in {repository_full_name} so the bot can push the version bump."
        )


def _checkout_pull_request_branch(pr) -> None:
    branch_ref = pr.head.ref
    _run_git("fetch", "origin", "main")
    _run_git("fetch", "origin", f"refs/heads/{branch_ref}:refs/remotes/origin/{branch_ref}")
    _run_git("checkout", "-B", branch_ref, f"refs/remotes/origin/{branch_ref}")
    _run_git("reset", "--hard", pr.head.sha)


def _is_main_ancestor_of_head() -> bool:
    result = subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"], check=False)
    return result.returncode == 0


def _wait_for_head_sha(repo, pr_number: int, expected_head_sha: str, previous_head_sha: str | None = None) -> None:
    for _ in range(HEAD_UPDATE_MAX_POLLS):
        pr = repo.get_pull(pr_number)
        current_head_sha = pr.head.sha
        if current_head_sha == expected_head_sha:
            return
        if previous_head_sha is not None and current_head_sha != previous_head_sha:
            raise click.ClickException(
                f"Pull request #{pr_number} head changed to unexpected commit {current_head_sha} while waiting for {expected_head_sha}."
            )
        time.sleep(READY_CHECK_POLL_INTERVAL_SECONDS)

    raise click.ClickException(f"Timed out waiting for pull request #{pr_number} to reach commit {expected_head_sha}.")


def _tidy_pull_request(repo, pr_number: int, repository_full_name: str):
    pr = repo.get_pull(pr_number)
    _validate_pull_request_state(pr, repository_full_name)
    original_head_sha = pr.head.sha

    if pr.draft:
        click.echo(f"Marking pull request #{pr.number} ready for review.")
        pr.mark_ready_for_review()
        pr = repo.get_pull(pr_number)

    _checkout_pull_request_branch(pr)

    if not _is_main_ancestor_of_head():
        click.echo(f"Updating pull request #{pr.number} with main.")
        pr.update_branch(expected_head_sha=pr.head.sha)
        previous_head_sha = pr.head.sha
        for _ in range(HEAD_UPDATE_MAX_POLLS):
            time.sleep(READY_CHECK_POLL_INTERVAL_SECONDS)
            pr = repo.get_pull(pr_number)
            if pr.head.sha != previous_head_sha:
                break
        else:
            raise click.ClickException(f"Timed out waiting for pull request #{pr.number} branch update.")
        _checkout_pull_request_branch(pr)

    return repo.get_pull(pr_number), original_head_sha


def _required_check_names(branch) -> set[str]:
    if not getattr(branch, "protected", False):
        return set()

    try:
        required_status_checks = branch.get_required_status_checks()
    except GithubException as exc:
        if exc.status == 404:
            return set()
        raise

    names = set(required_status_checks.contexts or [])
    for check in getattr(required_status_checks, "checks", []) or []:
        if isinstance(check, tuple):
            names.add(str(check[0]))
            continue
        if isinstance(check, dict):
            name = check.get("context") or check.get("name")
            if name:
                names.add(str(name))
            continue
        name = getattr(check, "context", None) or getattr(check, "name", None)
        if name:
            names.add(str(name))

    return names


def _required_approving_review_count(branch) -> int:
    if not getattr(branch, "protected", False):
        return 0

    try:
        required_reviews = branch.get_required_pull_request_reviews()
    except GithubException as exc:
        if exc.status == 404:
            return 0
        raise

    return int(required_reviews.required_approving_review_count or 0)


def _latest_review_states(pr) -> dict[str, str]:
    states: dict[str, str] = {}
    for review in pr.get_reviews():
        reviewer = review.user.login if review.user is not None else None
        if reviewer is None:
            continue
        states[reviewer] = review.state
    return states


def _evaluate_required_checks(repo, pr, branch) -> tuple[str, str]:
    required_check_names = _required_check_names(branch)
    if not required_check_names:
        return "pass", "No required status checks configured."

    commit = repo.get_commit(pr.head.sha)
    check_runs = {}
    for check_run in commit.get_check_runs():
        check_runs.setdefault(check_run.name, check_run)

    statuses = {}
    for status in commit.get_statuses():
        statuses.setdefault(status.context, status)

    waiting_for_anything = False
    for check_name in sorted(required_check_names):
        if check_name in check_runs:
            check_run = check_runs[check_name]
            if check_run.status in PENDING_CHECK_STATUSES or check_run.conclusion is None:
                waiting_for_anything = True
                continue
            if check_run.conclusion not in SUCCESSFUL_CHECK_CONCLUSIONS:
                return "fail", f"Required check run {check_name!r} concluded with {check_run.conclusion!r}."
            continue

        if check_name in statuses:
            status = statuses[check_name]
            if status.state == "pending":
                waiting_for_anything = True
                continue
            if status.state != "success":
                return "fail", f"Required status {check_name!r} completed with state {status.state!r}."
            continue

        return "wait", f"Waiting for required status check {check_name!r} to appear for commit {pr.head.sha}."

    if waiting_for_anything:
        return "wait", "Waiting for required checks to complete."

    return "pass", "Required checks passed."


def _evaluate_pull_request_requirements(repo, pr, branch, expected_head_sha: str) -> tuple[str, str]:
    _validate_pull_request_state(pr, repo.full_name)
    if pr.draft:
        return "fail", f"Pull request #{pr.number} is still a draft."
    if pr.head.sha != expected_head_sha:
        return "fail", f"Pull request #{pr.number} head changed to {pr.head.sha}."

    mergeable_state = pr.mergeable_state
    if pr.mergeable is None or mergeable_state in PENDING_MERGEABLE_STATES:
        return "wait", f"Waiting for GitHub to finalize mergeability ({mergeable_state!r})."

    if pr.mergeable is False:
        return "fail", f"Pull request #{pr.number} is not mergeable ({mergeable_state!r})."

    check_state, check_message = _evaluate_required_checks(repo, pr, branch)
    if check_state != "pass":
        return check_state, check_message

    required_approvals = _required_approving_review_count(branch)
    latest_review_states = _latest_review_states(pr)
    if any(state == "CHANGES_REQUESTED" for state in latest_review_states.values()):
        return "fail", f"Pull request #{pr.number} still has changes requested."

    approval_count = sum(1 for state in latest_review_states.values() if state == "APPROVED")
    if approval_count < required_approvals:
        return "fail", (
            f"Pull request #{pr.number} has {approval_count} approving reviews, "
            f"but {required_approvals} are required."
        )

    if mergeable_state not in {"clean", "has_hooks", "unstable"}:
        return "fail", f"Pull request #{pr.number} has unexpected mergeable state {mergeable_state!r}."

    return "pass", f"Pull request #{pr.number} satisfies merge requirements."


def _wait_for_pull_request_requirements(repo, pr_number: int, expected_head_sha: str):
    branch = repo.get_branch("main")
    for _ in range(READY_CHECK_MAX_POLLS):
        pr = repo.get_pull(pr_number)
        requirement_state, message = _evaluate_pull_request_requirements(repo, pr, branch, expected_head_sha)
        if requirement_state == "pass":
            click.echo(message)
            return pr
        if requirement_state == "fail":
            raise click.ClickException(message)
        click.echo(message)
        time.sleep(READY_CHECK_POLL_INTERVAL_SECONDS)

    raise click.ClickException(f"Timed out waiting for pull request #{pr_number} requirements to pass.")


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


@click.command(name="merge-pr")
def merge_pr() -> None:
    pr_number = int(_require_env("PR_NUMBER"))
    commenter_login = _require_env("MERGE_COMMENTER")
    github_token = _require_env("GITHUB_TOKEN")
    repository_full_name = _require_env("GITHUB_REPOSITORY")

    click.echo(f"Processing merge request for PR #{pr_number} in {repository_full_name}.")

    github_client = Github(github_token)
    repo = github_client.get_repo(repository_full_name)

    _validate_merge_commenter(repo, commenter_login)

    pr, initial_head_sha = _tidy_pull_request(repo, pr_number, repository_full_name)
    expected_head_sha = pr.head.sha
    if expected_head_sha != initial_head_sha:
        click.echo(f"Pull request #{pr_number} head changed from {initial_head_sha} to {expected_head_sha} during tidy-up.")

    _wait_for_pull_request_requirements(repo, pr_number, expected_head_sha)

    changed_paths = sorted(file.filename for file in repo.get_pull(pr_number).get_files())
    _configure_git_identity()
    bump_version(changed_paths=changed_paths, pr_number=pr_number, commit_changes=True)

    pushed_head_sha = _run_git("rev-parse", "HEAD", capture_output=True).stdout.strip()
    click.echo(f"Pushing version bump commit {pushed_head_sha} to {pr.head.ref}.")
    _run_git("push", "origin", f"HEAD:refs/heads/{pr.head.ref}")
    _wait_for_head_sha(repo, pr_number, pushed_head_sha, previous_head_sha=expected_head_sha)

    _wait_for_pull_request_requirements(repo, pr_number, pushed_head_sha)

    merge_status = repo.get_pull(pr_number).merge(merge_method="squash", sha=pushed_head_sha)
    if not merge_status.merged:
        raise click.ClickException(f"Failed to merge pull request #{pr_number}: {merge_status.message}")

    click.echo(f"Pull request #{pr_number} merged with squash.")


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
