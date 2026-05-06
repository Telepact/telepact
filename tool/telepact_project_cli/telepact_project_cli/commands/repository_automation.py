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

import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import click
import yaml
from github import Github, GithubException
from github.PullRequest import PullRequest

from .doc_versions import _read_go_module_path, _read_maven_gav, _read_package_json_name, _read_pyproject_name
from .project_version import _bump_version, create_version_bump_commit
from ..release_plan import (
    ReleaseManifest,
    compute_release_manifest_from_git,
    find_repo_root,
    load_release_target_rules,
    render_release_manifest_for_stdout,
    render_release_manifest_from_git,
    resolve_publish_targets,
)

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
RELEASE_MANIFEST_ASSET_NAME = "release-manifest.json"
MAIN_BRANCH = "main"
WAIT_TIMEOUT_SECONDS = 20 * 60  # 20 minutes
WAIT_INTERVAL_SECONDS = 10
MERGE_ALLOWED_PERMISSIONS = {"write", "maintain", "admin"}
MERGE_READY_LABEL = "Merge Ready"
MERGE_READY_LABEL_COLOR = "0e8a16"
MERGE_TRIGGER_COMMENT = "/merge"
VERSION_BUMP_BRANCH_PREFIX = "version-bump/"
PENDING_MERGEABLE_STATES = {"unknown"}
PENDING_CHECK_STATES = {"expected", "pending", "queued", "requested", "waiting", "in_progress"}
FAILED_COMBINED_STATUS_STATES = {"error", "failure"}
# GitHub check runs treat "neutral" and "skipped" as completed non-failures, while
# interrupted or incomplete conclusions such as "cancelled", "timed_out",
# "stale", and "action_required" should stop merge-pr immediately.
FAILED_CHECK_RUN_CONCLUSIONS = {"action_required", "cancelled", "failure", "startup_failure", "stale", "timed_out"}
SUCCESSFUL_CHECK_RUN_CONCLUSIONS = {"neutral", "skipped", "success"}

AUTOMERGE_ALLOWED_AUTHORS = ["dependabot[bot]"]
# Matches PR numbers appended by GitHub squash merges, e.g. "Bump version to 1.2.3 (#123)".
SQUASH_PR_NUMBER_RE = re.compile(r"\(#(?P<pr_number>\d+)\)$")

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


def _read_pubspec_name(pubspec_path: Path) -> str:
    try:
        data = yaml.safe_load(pubspec_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise click.ClickException(f"File not found: {pubspec_path}") from exc

    if not isinstance(data, dict):
        raise click.ClickException(f"Invalid YAML object in {pubspec_path}")

    name = data.get("name")
    if not isinstance(name, str) or not name:
        raise click.ClickException(f"Missing/invalid package name in {pubspec_path}")
    return name


def _release_target_details(repo_root: Path, target: str) -> tuple[str, str, str]:
    match target:
        case "go":
            return ("Library (Go)", _read_go_module_path(repo_root / "lib/go/go.mod"), "Go module")
        case "java":
            package_name, _ = _read_maven_gav(repo_root / "lib/java/pom.xml")
            return ("Library (Java)", package_name, "Maven Central")
        case "py":
            return ("Library (Python)", _read_pyproject_name(repo_root / "lib/py/pyproject.toml"), "PyPI")
        case "ts":
            return ("Library (TypeScript)", _read_package_json_name(repo_root / "lib/ts/package.json"), "npm")
        case "dart":
            return ("Binding (Dart)", _read_pubspec_name(repo_root / "bind/dart/pubspec.yaml"), "GitHub release assets")
        case "cli":
            return ("SDK (CLI)", _read_pyproject_name(repo_root / "sdk/cli/pyproject.toml"), "PyPI")
        case "console":
            return ("SDK (Console)", _read_package_json_name(repo_root / "sdk/console/package.json"), "npm")
        case "prettier":
            return ("SDK (Prettier)", _read_package_json_name(repo_root / "sdk/prettier/package.json"), "npm")
        case _:
            return (target, target, "Release assets")


def _format_release_target(repo_root: Path, target: str) -> str:
    label, package_name, registry = _release_target_details(repo_root, target)
    return f"- **{label}** — `{package_name}` ({registry})"


def _build_release_body(
    repo_root: Path,
    *,
    pr_title: str,
    pr_number: int | None,
    pr_url: str | None,
    direct_targets: list[str],
    release_targets: list[str],
) -> str:
    rules = load_release_target_rules(repo_root).projects
    direct_target_set = set(direct_targets)
    dependency_targets = [target for target in release_targets if target not in direct_target_set]

    direct_lines = [_format_release_target(repo_root, target) for target in direct_targets] or ["(None)"]

    def _dependency_reason(target: str) -> str:
        upstream_targets = sorted(source for source in direct_targets if target in rules[source].is_dependency_for)
        if not upstream_targets:
            return "dependency-triggered republish; usually no extra review beyond the underlying dependency update."
        upstream_labels = ", ".join(_release_target_details(repo_root, source)[0] for source in upstream_targets)
        return (
            f"dependency-triggered republish from {upstream_labels}; "
            "usually no extra review beyond the underlying dependency update."
        )

    republish_lines = [
        f"{_format_release_target(repo_root, target)} — {_dependency_reason(target)}"
        for target in dependency_targets
    ] or ["(None)"]

    summary_lines = [
        (
            f"{_format_release_target(repo_root, target)} — "
            "direct change; review if you use this package directly."
        )
        if target in direct_target_set
        else f"{_format_release_target(repo_root, target)} — {_dependency_reason(target)}"
        for target in release_targets
    ] or ["(None)"]

    heading = f"## {pr_title}"
    if pr_number is not None and pr_url:
        heading = f"{heading} [(#{pr_number})]({pr_url})"

    return (
        f"{heading}\n\n"
        "### Direct package changes\n"
        f"{chr(10).join(direct_lines)}\n\n"
        "### Dependency-triggered republishes\n"
        f"{chr(10).join(republish_lines)}\n\n"
        "### Published package summary\n"
        f"{chr(10).join(summary_lines)}"
    ).strip()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable is not set.")
    return value


def _write_github_outputs(github_output_path: Path | None, outputs: dict[str, str | int | bool]) -> None:
    lines = []
    for key, value in outputs.items():
        if isinstance(value, bool):
            rendered_value = "true" if value else "false"
        else:
            rendered_value = str(value)
        lines.append(f"{key}={rendered_value}")

    rendered_outputs = "\n".join(lines)
    if github_output_path is not None:
        github_output_path.parent.mkdir(parents=True, exist_ok=True)
        github_output_path.write_text(rendered_outputs + "\n", encoding="utf-8")
    else:
        click.echo(rendered_outputs)


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


def _checkout_pr_branch(head_ref: str) -> None:
    remote_ref = f"refs/remotes/origin/{head_ref}"
    _git("fetch", "origin", f"refs/heads/{head_ref}:{remote_ref}")
    _git("checkout", "-B", head_ref, remote_ref)


def _push_current_branch(head_ref: str) -> None:
    _git("push", "origin", f"HEAD:{head_ref}")


def _commenter_permission(repo, commenter_login: str) -> str:
    if not repo.has_in_collaborators(commenter_login):
        raise click.ClickException(f"User @{commenter_login} is not a repository collaborator.")

    commenter_permission = repo.get_collaborator_permission(commenter_login)
    if commenter_permission not in MERGE_ALLOWED_PERMISSIONS:
        raise RuntimeError(f"User @{commenter_login} does not have permission to merge pull requests.")

    return commenter_permission


def _label_names(issue) -> set[str]:
    return {label.name for label in getattr(issue, "labels", []) if getattr(label, "name", None)}


def _ensure_merge_ready_label(repo) -> None:
    try:
        repo.get_label(MERGE_READY_LABEL)
    except GithubException as exc:
        if exc.status != 404:
            raise
        repo.create_label(
            name=MERGE_READY_LABEL,
            color=MERGE_READY_LABEL_COLOR,
            description="Ready for merge queue processing.",
        )


def _merge_ready_label(repo):
    try:
        return repo.get_label(MERGE_READY_LABEL)
    except GithubException as exc:
        if exc.status != 404:
            raise
        return None


def _add_merge_ready_label(repo, pr_number: int) -> None:
    issue = repo.get_issue(pr_number)
    if issue.pull_request is None:
        raise RuntimeError(f"Issue #{pr_number} is not a pull request.")

    _ensure_merge_ready_label(repo)
    if MERGE_READY_LABEL not in _label_names(issue):
        issue.add_to_labels(MERGE_READY_LABEL)


def _remove_merge_ready_label(repo, pr_number: int) -> None:
    issue = repo.get_issue(pr_number)
    if MERGE_READY_LABEL in _label_names(issue):
        issue.remove_from_labels(MERGE_READY_LABEL)


def _open_merge_ready_pr_numbers(repo) -> list[int]:
    merge_ready_label = _merge_ready_label(repo)
    if merge_ready_label is None:
        return []

    merge_ready_numbers = []
    for issue in repo.get_issues(state="open", labels=[merge_ready_label]):
        if issue.pull_request is None:
            continue
        if MERGE_READY_LABEL in _label_names(issue):
            merge_ready_numbers.append(issue.number)
    return sorted(merge_ready_numbers)


def _next_merge_ready_pr_number(repo) -> int | None:
    merge_ready_numbers = _open_merge_ready_pr_numbers(repo)
    if not merge_ready_numbers:
        return None
    return merge_ready_numbers[0]


def _latest_merge_commenter_login(repo, pr_number: int) -> str:
    issue = repo.get_issue(pr_number)
    latest_commenter_login = None
    for comment in issue.get_comments():
        if (comment.body or "").strip() == MERGE_TRIGGER_COMMENT and comment.user is not None:
            latest_commenter_login = comment.user.login

    if latest_commenter_login is None:
        raise RuntimeError(f"Pull request #{pr_number} does not have a {MERGE_TRIGGER_COMMENT!r} trigger comment.")

    return latest_commenter_login


def _wait_for_pr_stable(repo, pr_number: int, expected_head_sha: str) -> PullRequest:
    deadline = time.monotonic() + WAIT_TIMEOUT_SECONDS
    while True:
        pr = repo.get_pull(pr_number)
        if pr.state != "open":
            raise RuntimeError(f"Pull request #{pr.number} is not open.")
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


def _head_commit_subject() -> str:
    return _git("log", "-1", "--format=%s", capture_output=True)


def _head_commit_pr_number() -> int | None:
    match = SQUASH_PR_NUMBER_RE.search(_head_commit_subject())
    if match is None:
        return None
    return int(match.group("pr_number"))


def _release_pr_metadata(repo, default_title: str) -> tuple[str, int | None, str | None]:
    pr_number = _head_commit_pr_number()
    if pr_number is None:
        return (default_title, None, None)
    try:
        pr = repo.get_pull(pr_number)
    except GithubException:
        return (default_title, pr_number, None)
    return (pr.title, pr.number, pr.html_url)


def _read_release_event_payload(event_path: Path) -> dict:
    try:
        data = json.loads(event_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise click.ClickException(f"GitHub event payload not found: {event_path}") from exc
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON in GitHub event payload {event_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise click.ClickException(f"GitHub event payload must be a JSON object: {event_path}")
    return data


def _release_manifest_asset_api_url(event_path: Path) -> str:
    event = _read_release_event_payload(event_path)
    release = event.get("release")
    if not isinstance(release, dict):
        raise click.ClickException("GitHub event payload does not include a release object.")
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        raise click.ClickException("GitHub release payload field 'assets' must be a list.")

    asset = next(
        (
            item
            for item in assets
            if isinstance(item, dict) and item.get("name") == RELEASE_MANIFEST_ASSET_NAME and isinstance(item.get("url"), str)
        ),
        None,
    )
    if asset is None:
        raise click.ClickException(f"{RELEASE_MANIFEST_ASSET_NAME} asset is missing from the release.")

    return asset["url"]


def _download_release_manifest_payload(event_path: Path, github_token: str) -> bytes:
    asset_url = _release_manifest_asset_api_url(event_path)
    request = urllib.request.Request(
        asset_url,
        headers={
            "Accept": "application/octet-stream",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise click.ClickException(f"Failed to download {RELEASE_MANIFEST_ASSET_NAME}: {exc}") from exc


def _parse_release_manifest_payload(payload: bytes) -> ReleaseManifest:
    try:
        data = json.loads(payload.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise click.ClickException(f"{RELEASE_MANIFEST_ASSET_NAME} is not valid UTF-8 JSON.") from exc
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"{RELEASE_MANIFEST_ASSET_NAME} is not valid JSON: {exc}") from exc
    return ReleaseManifest.from_dict(data)


def _process_merge_ready_pull_request(repo, pr_number: int) -> None:
    commenter_login = _latest_merge_commenter_login(repo, pr_number)
    commenter_permission = _commenter_permission(repo, commenter_login)
    is_admin = commenter_permission == "admin"

    click.echo(f"Processing merge-ready pull request #{pr_number} requested by @{commenter_login}.")

    pr = repo.get_pull(pr_number)
    if pr.state != "open":
        click.echo(f"Removing {MERGE_READY_LABEL!r} from pull request #{pr.number} because it is not open.")
        _remove_merge_ready_label(repo, pr.number)
        return
    expected_head_sha = pr.head.sha
    pr = _wait_for_pr_stable(repo, pr_number, expected_head_sha)
    _validate_merge_request(pr, is_admin)
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

    _verify_pull_request_ci(repo, pr_number, expected_head_sha)

    merge_result = pr.merge(merge_method="squash", sha=expected_head_sha)
    if not merge_result.merged:
        raise RuntimeError(f"Failed to merge pull request #{pr.number}: {merge_result.message}")

    _remove_merge_ready_label(repo, pr.number)
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
    release_manifest = compute_release_manifest_from_git(Path("."))
    version = release_manifest.version
    direct_targets = list(release_manifest.direct_targets)
    release_targets = list(release_manifest.targets)

    print(f"release_targets: {release_targets}")
    print(f"version: {version}")

    tag_name = version
    release_name = version

    g = Github(token)
    repo = g.get_repo(repository)
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

    pr_title, pr_number, pr_url = _release_pr_metadata(repo, _head_commit_subject())
    final_release_body = _build_release_body(
        find_repo_root(Path(".")),
        pr_title=pr_title,
        pr_number=pr_number,
        pr_url=pr_url,
        direct_targets=direct_targets,
        release_targets=release_targets,
    )

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
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / RELEASE_MANIFEST_ASSET_NAME
            manifest_path.write_text(render_release_manifest_for_stdout(release_manifest), encoding="utf-8")
            release.upload_asset(
                path=str(manifest_path),
                name=RELEASE_MANIFEST_ASSET_NAME,
                label=RELEASE_MANIFEST_ASSET_NAME,
            )
            asset_count += 1
            click.echo(f"Uploaded asset: {RELEASE_MANIFEST_ASSET_NAME}")

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
@click.option(
    "--release-manifest-path",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Path to the release-manifest.json asset to resolve publish targets from.",
)
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path), help="Write key=value lines for GitHub Actions outputs.")
def publish_targets(
    release_tag: str | None,
    release_body: str | None,
    release_manifest_path: Path | None,
    github_output: Path | None,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        effective_manifest_path = release_manifest_path
        if effective_manifest_path is None and os.getenv("GITHUB_EVENT_PATH"):
            github_token = _require_env("GITHUB_TOKEN")
            event_path = Path(_require_env("GITHUB_EVENT_PATH"))
            payload = _download_release_manifest_payload(event_path, github_token)
            manifest = _parse_release_manifest_payload(payload)
            effective_manifest_path = Path(temp_dir) / RELEASE_MANIFEST_ASSET_NAME
            effective_manifest_path.write_text(render_release_manifest_for_stdout(manifest), encoding="utf-8")

        outputs = resolve_publish_targets(
            Path("."),
            release_tag=release_tag,
            release_body=release_body,
            release_manifest_path=effective_manifest_path,
        )

        lines = [f"{key}={'true' if value else 'false'}" for key, value in outputs.items()]
        if github_output is not None:
            github_output.parent.mkdir(parents=True, exist_ok=True)
            github_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            click.echo("\n".join(lines))


@click.command(name="print-release-manifest")
@click.option("--ref", default="HEAD", help="Git ref to evaluate for release target computation.")
def print_release_manifest(ref: str) -> None:
    click.echo(render_release_manifest_from_git(Path("."), ref=ref))


@click.command(name="open-version-bump-pr")
def open_version_bump_pr() -> None:
    github_token = _require_env("GITHUB_TOKEN")
    github_repository = _require_env("GITHUB_REPOSITORY")

    repo_root = find_repo_root(Path("."))
    current_version = (repo_root / "VERSION.txt").read_text(encoding="utf-8").strip()
    github_client = Github(github_token)
    repo = github_client.get_repo(github_repository)
    owner_login = repo.owner.login
    next_version = _bump_version(current_version)
    branch_name = f"{VERSION_BUMP_BRANCH_PREFIX}{next_version}"
    existing_pr = next(iter(repo.get_pulls(state="open", head=f"{owner_login}:{branch_name}", base=MAIN_BRANCH)), None)
    if existing_pr is not None:
        click.echo(f"Version bump pull request already exists: {existing_pr.html_url}")
        return

    _git("checkout", "-B", branch_name)
    new_version = create_version_bump_commit(compute_release_targets=False)
    _push_current_branch(branch_name)

    pr = repo.create_pull(
        title=f"Bump version to {new_version}",
        body="Automated version bump PR.",
        head=f"{owner_login}:{branch_name}",
        base=MAIN_BRANCH,
    )
    click.echo(f"Created version bump pull request: {pr.html_url}")


@click.command(name="mark-merge-ready")
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path), help="Write key=value lines for GitHub Actions outputs.")
def mark_merge_ready(github_output: Path | None) -> None:
    github_token = _require_env("GITHUB_TOKEN")
    github_repository = _require_env("GITHUB_REPOSITORY")
    commenter_login = _require_env("COMMENTER_LOGIN")
    pr_number = int(_require_env("PR_NUMBER"))

    repo = Github(github_token).get_repo(github_repository)
    _commenter_permission(repo, commenter_login)
    issue = repo.get_issue(pr_number)
    if issue.state != "open":
        raise RuntimeError(f"Pull request #{pr_number} is not open.")

    merge_ready_pr_numbers = set(_open_merge_ready_pr_numbers(repo))
    merge_ready_pr_numbers.add(pr_number)
    merge_ready_count = len(merge_ready_pr_numbers)
    skip_merge_loop = len(merge_ready_pr_numbers - {pr_number}) > 0

    _add_merge_ready_label(repo, pr_number)

    click.echo(f"Pull request #{pr_number} is labeled {MERGE_READY_LABEL!r}. Open merge-ready pull requests: {merge_ready_count}.")
    _write_github_outputs(
        github_output,
        {
            "skip_merge_loop": skip_merge_loop,
            "merge_ready_count": merge_ready_count,
        },
    )


@click.command(name="merge-pr")
def merge_pr() -> None:
    github_token = _require_env("GITHUB_TOKEN")
    github_repository = _require_env("GITHUB_REPOSITORY")
    repo = Github(github_token).get_repo(github_repository)
    failures: list[tuple[int, str]] = []

    while True:
        pr_number = _next_merge_ready_pr_number(repo)
        if pr_number is None:
            break

        try:
            _process_merge_ready_pull_request(repo, pr_number)
        except Exception as exc:
            click.echo(f"Failed to merge pull request #{pr_number}: {exc}")
            _remove_merge_ready_label(repo, pr_number)
            failures.append((pr_number, repr(exc)))

    if failures:
        failure_summary = "; ".join(f"#{pr_number}: {message}" for pr_number, message in failures)
        raise RuntimeError(f"Merge loop completed with failures: {failure_summary}")

    click.echo("No merge-ready pull requests remain.")


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
