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
from pathlib import Path

import click
from github import Github, GithubException

from ..constants import MAX_RELEASE_ASSETS, RELEASE_TARGET_ASSET_DIRECTORY_MAP
from ..git_helpers import git_stdout
from ..release_plan import find_repo_root, load_release_manifest, parse_legacy_release_info, resolve_publish_targets


def _load_release_metadata(repo_root: Path) -> tuple[str, int, list[str]] | None:
    manifest_file = repo_root / ".release" / "release-manifest.json"
    if manifest_file.exists():
        release_manifest = load_release_manifest(repo_root)
        version = release_manifest["version"]
        pr_number = int(release_manifest["pr_number"])
        release_targets = list(release_manifest.get("targets", []))
        click.echo("Loaded release metadata from .release/release-manifest.json")
        return version, pr_number, release_targets

    commit_message = git_stdout(["show", "-s", "--format=%s%n%b", "HEAD"], cwd=repo_root).strip()
    lines = commit_message.splitlines()
    legacy_info = parse_legacy_release_info(lines[0] if lines else "", "\n".join(lines[1:]))
    if legacy_info is None:
        return None

    version, release_targets = legacy_info
    pr_number_str = lines[0].rsplit("(#", 1)[-1].rstrip(")") if lines else ""
    click.echo("Loaded release metadata from legacy bump commit message")
    return version, int(pr_number_str), release_targets


def _release_body(pr_title: str, pr_number: int, pr_url: str, release_targets: list[str]) -> str:
    released_projects_text = "".join(f"- {target}\n" for target in release_targets) if release_targets else "(None)"
    return (
        f"## {pr_title} [(#{pr_number})]({pr_url})\n\n"
        f"### Released Projects\n"
        f"{released_projects_text}"
    ).strip()


def _upload_release_assets(release, release_targets: list[str]) -> None:
    asset_count = 0
    for target in release_targets:
        for asset_directory in RELEASE_TARGET_ASSET_DIRECTORY_MAP.get(target, []):
            if not os.path.exists(asset_directory):
                click.echo(f"Asset directory does not exist: {asset_directory} for target: {target}")
                continue

            for file_name in os.listdir(asset_directory):
                if asset_count >= MAX_RELEASE_ASSETS:
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


@click.command()
def release() -> None:
    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")
    if not token or not repository:
        click.echo("GITHUB_TOKEN and GITHUB_REPOSITORY environment variables must be set.")
        return

    repo_root = find_repo_root(Path("."))
    head_commit = git_stdout(["rev-parse", "HEAD"], cwd=repo_root).strip()

    metadata = _load_release_metadata(repo_root)
    if metadata is None:
        click.echo("No release manifest found and the last commit message does not match the expected legacy format.")
        return

    version, pr_number, release_targets = metadata
    github_client = Github(token)
    repo = github_client.get_repo(repository)
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
        except GithubException as exc:
            if exc.status != 404:
                raise
            repo.create_git_ref(ref=f"refs/tags/{go_module_tag}", sha=head_commit)
            click.echo(f"Created Go module tag: {go_module_tag}")

    final_release_body = _release_body(pr.title, pr_number, pr.html_url, release_targets)

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
        _upload_release_assets(release_obj, release_targets)
    except Exception as exc:
        click.echo(f"Failed to create release or upload assets: {exc}")


@click.command(name="publish-targets")
@click.option("--release-tag", default=None, help="Expected release tag/version for validation.")
@click.option("--release-body", default=None, help="Legacy fallback release body when no manifest exists.")
@click.option(
    "--github-output",
    default=None,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write key=value lines for GitHub Actions outputs.",
)
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
