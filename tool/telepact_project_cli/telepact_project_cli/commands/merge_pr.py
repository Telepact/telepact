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

import base64
import os
import shutil
import time
from pathlib import Path

import click
from github import Github, GithubException

from .project_version import bump_pull_request_version

ALLOWED_MERGE_PERMISSIONS = {"admin", "maintain", "write"}
PENDING_CHECK_STATES = {"expected", "pending", "queued", "in_progress", "requested", "waiting"}
SUCCESSFUL_CHECK_CONCLUSIONS = {"success", "neutral", "skipped"}
POLL_INTERVAL_SECONDS = 5
MAX_REQUIREMENT_POLLS = 60
MAX_BRANCH_UPDATE_POLLS = 24
MAX_MERGEABLE_POLLS = 12


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable not set.")
    return value


def _refresh_pr(repo, pr_number: int, expected_head_sha: str | None = None):
    pr = repo.get_pull(pr_number)
    if expected_head_sha is not None and pr.head.sha != expected_head_sha:
        raise click.ClickException(
            f"PR #{pr_number} head changed from {expected_head_sha} to {pr.head.sha} while merge-pr was running."
        )
    return pr


def _validate_pr_state(pr) -> None:
    if pr.state != "open":
        raise click.ClickException(f"PR #{pr.number} is not open.")
    if pr.base.ref != "main":
        raise click.ClickException(f"PR #{pr.number} must target main; found base branch {pr.base.ref!r}.")
    if pr.head.repo is None or pr.head.repo.full_name != pr.base.repo.full_name:
        raise click.ClickException(f"PR #{pr.number} must come from a writable branch in {pr.base.repo.full_name}.")


def _ensure_commenter_can_merge(repo, commenter: str) -> None:
    try:
        permission = repo.get_collaborator_permission(commenter)
    except GithubException as exc:
        if exc.status == 404:
            raise click.ClickException(f"User @{commenter} is not a repository member of {repo.full_name}.")
        raise
    if permission.lower() not in ALLOWED_MERGE_PERMISSIONS:
        raise click.ClickException(
            f"User @{commenter} is not allowed to merge PRs in {repo.full_name} (permission={permission})."
        )


def _required_check_names(required_status_checks) -> list[str]:
    if required_status_checks is None:
        return []

    names = set(required_status_checks.contexts or [])
    for check in getattr(required_status_checks, "checks", []) or []:
        if isinstance(check, tuple):
            names.add(check[0])
            continue
        if isinstance(check, str):
            names.add(check)
            continue
        for attr_name in ("context", "name"):
            value = getattr(check, attr_name, None)
            if isinstance(value, str) and value:
                names.add(value)
                break
    return sorted(names)


def _latest_review_states(pr) -> dict[str, str]:
    states: dict[str, str] = {}
    for review in pr.get_reviews():
        user = getattr(getattr(review, "user", None), "login", None)
        state = getattr(review, "state", None)
        if not user or not state:
            continue
        states[user] = state.upper()
    return states


def _validate_review_requirements(pr, required_reviews) -> None:
    if required_reviews is None:
        return

    latest_states = _latest_review_states(pr)
    approvers = sorted(user for user, state in latest_states.items() if state == "APPROVED")
    change_requesters = sorted(user for user, state in latest_states.items() if state == "CHANGES_REQUESTED")

    if change_requesters:
        raise click.ClickException(
            f"PR #{pr.number} has outstanding change requests from: {', '.join(change_requesters)}."
        )

    required_count = getattr(required_reviews, "required_approving_review_count", 0) or 0
    if len(approvers) < required_count:
        raise click.ClickException(
            f"PR #{pr.number} requires {required_count} approvals but only has {len(approvers)}."
        )


def _latest_check_run_by_name(commit) -> dict[str, object]:
    latest_runs: dict[str, object] = {}
    for check_run in commit.get_check_runs():
        current = latest_runs.get(check_run.name)
        if current is None or check_run.id > current.id:
            latest_runs[check_run.name] = check_run
    return latest_runs


def _sync_pull_request_head_to_worktree(repo, head_sha: str, repo_root: Path | str) -> None:
    repo_root = Path(repo_root).resolve()
    git_commit = repo.get_git_commit(head_sha)
    git_tree = repo.get_git_tree(git_commit.tree.sha, recursive=True)

    for child in repo_root.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    for element in git_tree.tree:
        if element.type != "blob":
            continue
        blob = repo.get_git_blob(element.sha)
        content = blob.content
        data = base64.b64decode(content) if blob.encoding == "base64" else content.encode("utf-8")
        path = repo_root / element.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def _evaluate_required_checks(commit, required_check_names: list[str]) -> tuple[list[str], list[str]]:
    pending: list[str] = []
    failed: list[str] = []
    if not required_check_names:
        return pending, failed

    statuses = {status.context: status.state.lower() for status in commit.get_statuses()}
    check_runs = _latest_check_run_by_name(commit)

    for check_name in required_check_names:
        if check_name in check_runs:
            check_run = check_runs[check_name]
            status = check_run.status.lower()
            conclusion = (check_run.conclusion or "").lower()
            if status != "completed":
                pending.append(check_name)
            elif conclusion not in SUCCESSFUL_CHECK_CONCLUSIONS:
                failed.append(f"{check_name} ({conclusion or 'unknown'})")
            continue

        state = statuses.get(check_name)
        if state is None or state in PENDING_CHECK_STATES:
            pending.append(check_name)
        elif state != "success":
            failed.append(f"{check_name} ({state})")

    return pending, failed


def _await_mergeable_pr(repo, pr_number: int, expected_head_sha: str):
    for _ in range(MAX_MERGEABLE_POLLS):
        pr = _refresh_pr(repo, pr_number, expected_head_sha)
        if pr.mergeable is not None and pr.mergeable_state != "unknown":
            return pr
        time.sleep(POLL_INTERVAL_SECONDS)
    raise click.ClickException(f"Timed out waiting for GitHub to compute mergeability for PR #{pr_number}.")


def verify_pr_requirements(repo, pr_number: int, expected_head_sha: str) -> object:
    pr = _refresh_pr(repo, pr_number, expected_head_sha)
    _validate_pr_state(pr)
    if pr.draft:
        raise click.ClickException(f"PR #{pr_number} is still a draft.")

    branch = repo.get_branch("main")
    try:
        protection = branch.get_protection()
    except GithubException as exc:
        if exc.status != 404:
            raise
        protection = None

    required_reviews = getattr(protection, "required_pull_request_reviews", None)
    required_status_checks = getattr(protection, "required_status_checks", None)
    required_check_names = _required_check_names(required_status_checks)

    last_pending: list[str] = []
    for _ in range(MAX_REQUIREMENT_POLLS):
        pr = _refresh_pr(repo, pr_number, expected_head_sha)
        _validate_pr_state(pr)
        _validate_review_requirements(pr, required_reviews)

        commit = repo.get_commit(expected_head_sha)
        pending_checks, failed_checks = _evaluate_required_checks(commit, required_check_names)
        if failed_checks:
            raise click.ClickException(
                f"Required checks failed for PR #{pr_number}: {', '.join(sorted(failed_checks))}."
            )
        if pending_checks:
            last_pending = pending_checks
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        pr = _await_mergeable_pr(repo, pr_number, expected_head_sha)
        if pr.mergeable is False:
            raise click.ClickException(f"PR #{pr_number} is not mergeable.")
        if pr.mergeable_state in {"behind", "blocked", "dirty", "draft"}:
            raise click.ClickException(
                f"PR #{pr_number} failed mergeability checks (state={pr.mergeable_state})."
            )
        return pr

    pending_summary = ", ".join(sorted(last_pending)) if last_pending else "required checks"
    raise click.ClickException(f"Timed out waiting for PR #{pr_number} checks to finish: {pending_summary}.")


def _wait_for_branch_update(repo, pr_number: int, previous_head_sha: str):
    for _ in range(MAX_BRANCH_UPDATE_POLLS):
        pr = repo.get_pull(pr_number)
        if pr.head.sha != previous_head_sha:
            return pr
        time.sleep(POLL_INTERVAL_SECONDS)
    raise click.ClickException(f"Timed out waiting for PR #{pr_number} to update with main.")


def _wait_for_ready_for_review(repo, pr_number: int):
    for _ in range(MAX_MERGEABLE_POLLS):
        pr = repo.get_pull(pr_number)
        if not pr.draft:
            return pr
        time.sleep(POLL_INTERVAL_SECONDS)
    raise click.ClickException(f"Timed out waiting for PR #{pr_number} to leave draft state.")


def _tidy_pull_request(repo, pr):
    _validate_pr_state(pr)

    if pr.draft:
        pr.mark_ready_for_review()
        pr = _wait_for_ready_for_review(repo, pr.number)

    main_sha = repo.get_branch("main").commit.sha
    comparison = repo.compare(main_sha, pr.head.sha)
    if comparison.behind_by > 0:
        previous_head_sha = pr.head.sha
        pr.update_branch(expected_head_sha=previous_head_sha)
        pr = _wait_for_branch_update(repo, pr.number, previous_head_sha)

    return pr


@click.command(name="merge-pr")
def merge_pr() -> None:
    commenter = _require_env("COMMENT_AUTHOR")
    pr_number = int(_require_env("PR_NUMBER"))
    token = _require_env("GITHUB_TOKEN")
    repository_name = _require_env("GITHUB_REPOSITORY")

    g = Github(token)
    repo = g.get_repo(repository_name)
    _ensure_commenter_can_merge(repo, commenter)

    pr = repo.get_pull(pr_number)
    _validate_pr_state(pr)
    pr = _tidy_pull_request(repo, pr)
    pr = verify_pr_requirements(repo, pr.number, pr.head.sha)
    _sync_pull_request_head_to_worktree(repo, pr.head.sha, ".")

    new_head_sha, new_version = bump_pull_request_version(repo, pr, ".")
    verify_pr_requirements(repo, pr.number, new_head_sha)

    merge_status = repo.get_pull(pr.number).merge(merge_method="squash", sha=new_head_sha)
    if not merge_status.merged:
        raise click.ClickException(f"Failed to merge PR #{pr.number}: {merge_status.message}")

    click.echo(f"Merged PR #{pr.number} as version {new_version}.")
