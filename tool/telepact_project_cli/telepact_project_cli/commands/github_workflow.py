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

import os
import subprocess
import sys
from pathlib import Path

import click
from github import Github, GithubException

from ..release_plan import load_release_manifest, parse_legacy_release_info, resolve_publish_targets


def _require_env(name: str, message: str) -> str:
    value = os.getenv(name)
    if not value:
        click.echo(message, err=True)
        raise click.Abort()
    return value


def _require_pr_number() -> int:
    pr_number_str = os.getenv("PR_NUMBER")
    if not pr_number_str:
        click.echo("PR_NUMBER environment variable not set.", err=True)
        sys.exit(1)
    return int(pr_number_str)


@click.command(name="github-labels")
def github_labels() -> None:
    project_label_map = {
        "lib/java": "java",
        "lib/py": "py",
        "lib/ts": "ts",
        "lib/go": "go",
        "bind/dart": "dart",
        "sdk/cli": "cli",
        "sdk/console": "console",
        "sdk/prettier": "prettier",
    }

    def get_modified_files(base_branch: str, head_sha: str) -> str:
        try:
            subprocess.run(["git", "fetch", "origin", base_branch], check=True)
            result = subprocess.run(
                ["git", "diff", "--name-only", f"origin/{base_branch}", head_sha],
                check=True,
                stdout=subprocess.PIPE,
            )
            return result.stdout.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            print(f"Error fetching or diffing: {e}")
            return ""

    def get_modified_project_labels(files: str) -> set[str]:
        tags = set()
        for file in files.split():
            for directory, tag in project_label_map.items():
                if file.startswith(directory):
                    tags.add(tag)
        return tags

    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number = _require_pr_number()
    base_branch = os.getenv("BASE_BRANCH")
    head_sha = os.getenv("HEAD_SHA")

    files = get_modified_files(base_branch, head_sha)
    print(f"Modified files: {files}")

    g = Github(token)
    repo = g.get_repo(repository)
    pr = repo.get_pull(pr_number)
    current_labels = {label.name for label in pr.get_labels()}
    new_labels = get_modified_project_labels(files)

    print(f"Labels to be added: {new_labels}")

    added_labels = []
    removed_labels = []
    for label in new_labels:
        if label not in current_labels:
            pr.add_to_labels(label)
            added_labels.append(label)

    for label in current_labels:
        if label not in new_labels and label in project_label_map.values():
            pr.remove_from_labels(label)
            removed_labels.append(label)

    print(
        f"Summary:\n  Added tags: {', '.join(added_labels) if added_labels else 'None'}\n"
        f"  Removed tags: {', '.join(removed_labels) if removed_labels else 'None'}"
    )


@click.command()
def release() -> None:
    release_target_asset_directory_map = {
        "java": ["lib/java/target/central-publishing"],
        "py": ["lib/py/dist"],
        "ts": ["lib/ts/dist-tgz"],
        "dart": ["bind/dart/dist"],
        "cli": ["sdk/cli/dist", "sdk/cli/dist-docker"],
        "console": ["sdk/console/dist-tgz", "sdk/console/dist-docker"],
        "prettier": ["sdk/prettier/dist-tgz"],
    }
    max_assets = 10

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
        commit_message = subprocess.run(
            ["git", "show", "-s", "--format=%s%n%b", "HEAD"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout.strip()
        print(f"commit_message: {commit_message}")
        lines = commit_message.splitlines()
        legacy_info = parse_legacy_release_info(lines[0] if lines else "", "\n".join(lines[1:]))
        if legacy_info is None:
            click.echo("No release manifest found and the last commit message does not match the expected legacy format.")
            return
        version, release_targets = legacy_info
        pr_number_str = lines[0].rsplit("(#", 1)[-1].rstrip(")") if lines else ""
        pr_number = int(pr_number_str)
        click.echo("Loaded release metadata from legacy bump commit message")

    print(f"release_targets: {release_targets}")
    print(f"version: {version}")
    print(f"pr_number: {pr_number}")

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
            tag=version,
            name=version,
            message=final_release_body,
            draft=False,
            prerelease=True,
            target_commitish=head_commit,
        )
        click.echo(f"Release created: {release.html_url}")

        asset_count = 0
        for target in release_targets:
            asset_directories = release_target_asset_directory_map.get(target, [])
            for asset_directory in asset_directories:
                if os.path.exists(asset_directory):
                    for file_name in os.listdir(asset_directory):
                        if asset_count >= max_assets:
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
@click.option("--release-body", default=None, help="Legacy fallback release body when no manifest exists.")
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
def automerge() -> None:
    automerge_allowed_authors = ["dependabot[bot]"]
    automerge_allowed_files = [
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

    pr_number = _require_pr_number()
    github_token = _require_env("GITHUB_TOKEN", "GITHUB_TOKEN environment variable is not set.")
    github_repository = _require_env(
        "GITHUB_REPOSITORY",
        "GITHUB_REPOSITORY environment variable is not set (e.g., 'owner/repo').",
    )

    print(f"Processing PR #{pr_number} in '{github_repository}'...")
    print(f"Hardcoded allowed authors for automerge: {', '.join(automerge_allowed_authors)}")

    g = Github(github_token)
    repo_obj = g.get_repo(github_repository)
    pr = repo_obj.get_pull(pr_number)

    pr_author_login = pr.user.login
    print(f"Pull Request #{pr_number} is authored by @{pr_author_login}")

    if pr_author_login not in automerge_allowed_authors:
        raise Exception(f"Author @{pr_author_login} is NOT on the hardcoded allow list. Aborting automerge.")
    print(f"Author @{pr_author_login} is on the allow list.")

    for f in pr.get_files():
        if f.status == "removed":
            raise Exception(f"Pull Request #{pr_number} contains removed files. Aborting automerge.")
        if f.filename not in automerge_allowed_files:
            raise Exception(
                f"Pull Request #{pr_number} contains changes in the file '{f.filename}' which is not allowed for automerge."
            )

    print("Approving Pull Request...")
    pr.create_review(event="APPROVE")
    print("Pull Request approved.")

    pr.enable_automerge(merge_method="SQUASH")
    print("Pull Request will be automerged when build succeeds.")
