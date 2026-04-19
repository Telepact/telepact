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
import contextlib
import click
import os
import sys
import tempfile
import time
from lxml import etree as ET
import json
import toml
from ruamel.yaml import YAML
import subprocess
from github import Github, GithubException, InputGitAuthor, InputGitTreeElement
from pathlib import Path

from .commands.consolidated_readme import consolidated_readme
from .commands.doc_versions import doc_versions, write_doc_versions
from .release_plan import (
    compute_release_manifest,
    load_release_manifest,
    parse_legacy_release_info,
    resolve_publish_targets,
    write_release_manifest,
)

yaml = YAML()
LICENSE_HEADER_IGNORE_FILE = ".license-header-ignore"
DEFAULT_BASE_BRANCH = "main"
MERGE_ALLOWED_PERMISSION_LEVELS = {"admin", "maintain", "write"}
PR_REQUIREMENTS_POLL_INTERVAL_SECONDS = 15
PR_REQUIREMENTS_MAX_POLLS = 120
PR_UPDATE_BRANCH_POLL_INTERVAL_SECONDS = 5
PR_UPDATE_BRANCH_MAX_POLLS = 60
BUMP_PROJECT_FILES = [
    'lib/java/pom.xml',
    'lib/py/pyproject.toml',
    'lib/ts/package.json',
    'bind/dart/pubspec.yaml',
    'bind/dart/package.json',
    'sdk/cli/pyproject.toml',
    'sdk/prettier/package.json',
    'sdk/console/package.json',
]
BUMP_COMMIT_AUTHOR = InputGitAuthor(
    "telepact-notary[bot]",
    "telepact-notary[bot]@users.noreply.github.com",
)


def _write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2) + "\n")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise click.ClickException(f"{name} environment variable is not set.")
    return value


def _load_pyproject() -> dict:
    with open("pyproject.toml", "r") as f:
        return toml.load(f)


def _project_version(data: dict) -> str:
    project = data.get("project", {})
    if "version" in project:
        return project["version"]
    return data["tool"]["poetry"]["version"]


def _set_project_version(data: dict, version: str) -> dict:
    project = data.get("project")
    if isinstance(project, dict) and "version" in project:
        project["version"] = version
        return data

    data["tool"]["poetry"]["version"] = version
    return data


def bump_version(version: str) -> str:
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"


def _license_header_supported(file_path: str) -> bool:
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)

    return (
        (file_name != 'pubspec.yaml' and file_extension in ['.py', '.java', '.ts', '.dart', '.sh', '.js', '.yaml', '.yml', '.html', '.css', '.svelte'])
        or file_name == 'Dockerfile'
        or file_name == 'Makefile'
    )


def _license_header_ignored(file_path: str) -> bool:
    path = Path(file_path)
    for directory in path.parents:
        if (directory / LICENSE_HEADER_IGNORE_FILE).exists():
            return True

    return False


def _get_repo_and_pr() -> tuple[Github, object, object, int]:
    github_token = _require_env('GITHUB_TOKEN')
    github_repository = _require_env('GITHUB_REPOSITORY')
    pr_number = int(_require_env('PR_NUMBER'))

    github_client = Github(github_token)
    repo = github_client.get_repo(github_repository)
    pr = repo.get_pull(pr_number)
    return github_client, repo, pr, pr_number


def _refresh_pull_request(repo, pr_number: int):
    return repo.get_pull(pr_number)


def _validate_open_main_branch_pull_request(repo, pr, pr_number: int) -> None:
    if pr.state != 'open':
        raise click.ClickException(f"Pull request #{pr_number} is not open.")
    if pr.base.ref != DEFAULT_BASE_BRANCH:
        raise click.ClickException(
            f"Pull request #{pr_number} must target '{DEFAULT_BASE_BRANCH}', found '{pr.base.ref}'."
        )
    if pr.head.repo is None or pr.head.repo.full_name != repo.full_name:
        raise click.ClickException(
            f"Pull request #{pr_number} must use a branch in '{repo.full_name}'."
        )


@contextlib.contextmanager
def _pushd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _get_required_context_results_for_commit(commit) -> dict[str, str]:
    results: dict[str, str] = {}

    combined_status = commit.get_combined_status()
    for status in combined_status.statuses:
        state = (status.state or "").lower()
        if state:
            results[status.context] = state

    for check_run in commit.get_check_runs():
        status = (check_run.status or "").lower()
        conclusion = (check_run.conclusion or "").lower()
        if status == "completed":
            results[check_run.name] = conclusion or "failure"
        else:
            results[check_run.name] = status or "queued"

    return results


def _get_pending_required_contexts(required_contexts: list[str], results: dict[str, str]) -> list[str]:
    pending_states = {"queued", "in_progress", "pending", "requested", "waiting"}
    pending = []
    for context in required_contexts:
        state = results.get(context)
        if state is None or state in pending_states:
            pending.append(context)
    return pending


def _get_failed_required_contexts(required_contexts: list[str], results: dict[str, str]) -> list[str]:
    acceptable_states = {"success", "neutral", "skipped"}
    pending_states = {"queued", "in_progress", "pending", "requested", "waiting"}
    failed = []
    for context in required_contexts:
        state = results.get(context)
        if state is None or state in pending_states or state in acceptable_states:
            continue
        failed.append(f"{context}={state}")
    return failed


def _commit_files_via_git_data_api(repo, branch_name: str, head_sha: str, edited_paths: list[str], commit_message: str) -> str:
    head_commit = repo.get_git_commit(head_sha)
    tree_elements: list[InputGitTreeElement] = []
    unique_edited_paths: list[str] = []
    seen_paths: set[str] = set()
    for repo_relative_path in edited_paths:
        if repo_relative_path in seen_paths:
            continue
        seen_paths.add(repo_relative_path)
        unique_edited_paths.append(repo_relative_path)

    for repo_relative_path in unique_edited_paths:
        file_content = Path(repo_relative_path).read_text(encoding="utf-8")
        blob = repo.create_git_blob(file_content, "utf-8")
        tree_elements.append(
            InputGitTreeElement(
                path=repo_relative_path,
                mode="100644",
                type="blob",
                sha=blob.sha,
            )
        )

    new_tree = repo.create_git_tree(tree_elements, base_tree=head_commit.tree)
    new_commit = repo.create_git_commit(
        commit_message,
        new_tree,
        [head_commit],
        author=BUMP_COMMIT_AUTHOR,
        committer=BUMP_COMMIT_AUTHOR,
    )
    repo.get_git_ref(f"heads/{branch_name}").edit(new_commit.sha, force=False)
    return new_commit.sha


def _materialize_pull_request_head(repo, head_sha: str, destination: Path) -> None:
    head_commit = repo.get_git_commit(head_sha)
    git_tree = repo.get_git_tree(head_commit.tree.sha, recursive=True)

    for entry in git_tree.tree:
        if entry.type != "blob":
            continue

        target_path = destination / entry.path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        blob = repo.get_git_blob(entry.sha)
        if blob.encoding != "base64":
            raise click.ClickException(
                f"Unsupported blob encoding '{blob.encoding}' for {entry.path}."
            )
        target_path.write_bytes(base64.b64decode(blob.content))


@click.group()
def main() -> None:
    pass


@click.command()
def get() -> None:
    if os.path.exists("pom.xml"):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse("pom.xml", parser)
        root = tree.getroot()
        version = root.find("{http://maven.apache.org/POM/4.0.0}version").text
        click.echo(version, nl=False)
    elif os.path.exists("package.json"):
        with open("package.json", "r") as f:
            data = json.load(f)
        version = data["version"]
        click.echo(version, nl=False)
    elif os.path.exists("pyproject.toml"):
        data = _load_pyproject()
        version = _project_version(data)
        click.echo(version, nl=False)
    elif os.path.exists("pubspec.yaml"):
        with open("pubspec.yaml", "r") as f:
            data = yaml.load(f)
        version = data["version"]
        click.echo(version, nl=False)
    else:
        click.echo("No supported project file found.", nl=False)


@click.command()
@click.argument('version')
def set_version(version: str) -> None:
    updated = False

    if os.path.exists("pom.xml"):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse("pom.xml", parser)
        root = tree.getroot()
        root.find("{http://maven.apache.org/POM/4.0.0}version").text = version
        tree.write("pom.xml", xml_declaration=True, encoding='utf-8', pretty_print=True)
        click.echo(f"Set pom.xml to version {version}")
        updated = True

    if os.path.exists("package.json"):
        with open("package.json", "r") as f:
            data = json.load(f)
        data["version"] = version
        _write_json("package.json", data)
        click.echo(f"Set package.json to version {version}")
        updated = True

    if os.path.exists("pyproject.toml"):
        data = _set_project_version(_load_pyproject(), version)
        with open("pyproject.toml", "w") as f:
            toml.dump(data, f)
        click.echo(f"Set pyproject.toml to version {version}")
        updated = True

    if os.path.exists("pubspec.yaml"):
        with open("pubspec.yaml", "r") as f:
            data = yaml.load(f)
        data["version"] = version
        with open("pubspec.yaml", "w") as f:
            yaml.dump(data, f)
        click.echo(f"Set pubspec.yaml to version {version}")
        updated = True

    if not updated:
        click.echo("No supported project file found.")


@click.command()
def bump() -> None:
    _, repo, pr, pr_number = _get_repo_and_pr()
    _validate_open_main_branch_pull_request(repo, pr, pr_number)

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_repo_root = Path(tmp_dir)
        _materialize_pull_request_head(repo, pr.head.sha, temp_repo_root)
        history_repo_root = Path.cwd()

        with _pushd(temp_repo_root):
            version_file = Path('VERSION.txt')
            if not version_file.exists():
                raise click.ClickException(f"Version file {version_file} does not exist.")

            version = version_file.read_text(encoding='utf-8').strip()
            new_version = bump_version(version)
            version_file.write_text(new_version, encoding='utf-8')
            click.echo(f"Updated version file {version_file} to version {new_version}")

            edited_files = [str(version_file)]

            for project_file in BUMP_PROJECT_FILES:
                if os.path.exists(project_file):
                    if project_file.endswith("pom.xml"):
                        parser = ET.XMLParser(remove_blank_text=True)
                        tree = ET.parse(project_file, parser)
                        root = tree.getroot()
                        root.find("{http://maven.apache.org/POM/4.0.0}version").text = new_version
                        tree.write(project_file, xml_declaration=True, encoding='utf-8', pretty_print=True)
                    elif project_file.endswith("package.json"):
                        with open(project_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        data["version"] = new_version
                        _write_json(project_file, data)
                    elif project_file.endswith("pyproject.toml"):
                        with open(project_file, 'r', encoding='utf-8') as f:
                            data = toml.load(f)
                        data = _set_project_version(data, new_version)
                        with open(project_file, 'w', encoding='utf-8') as f:
                            toml.dump(data, f)
                    elif project_file.endswith("pubspec.yaml"):
                        with open(project_file, 'r', encoding='utf-8') as f:
                            data = yaml.load(f)
                        data["version"] = new_version
                        with open(project_file, 'w', encoding='utf-8') as f:
                            yaml.dump(data, f)
                    else:
                        raise click.ClickException(f"Unsupported project file type: {project_file}")
                    click.echo(f"Updated {project_file} to version {new_version}")
                    edited_files.append(project_file)
                else:
                    click.echo(f"Project file {project_file} does not exist.")

            npm_lock_directories: set[str] = set()
            uv_lock_directories: set[str] = set()
            dart_lock_directories: set[str] = set()
            for project_file in BUMP_PROJECT_FILES:
                project_directory = os.path.dirname(project_file)
                if (
                    project_file.endswith("package.json")
                    and project_directory not in npm_lock_directories
                    and os.path.exists(os.path.join(project_directory, "package-lock.json"))
                ):
                    npm_lock_directories.add(project_directory)
                    subprocess.run(
                        [
                            "npm",
                            "install",
                            "--package-lock-only",
                            "--ignore-scripts",
                            "--no-audit",
                            "--no-fund",
                        ],
                        cwd=project_directory,
                        check=True,
                    )
                    edited_files.append(os.path.join(project_directory, "package-lock.json"))
                    click.echo(f"Updated package-lock.json in {project_directory}")

                if (
                    project_file.endswith("pyproject.toml")
                    and project_directory not in uv_lock_directories
                    and os.path.exists(os.path.join(project_directory, "uv.lock"))
                ):
                    uv_lock_directories.add(project_directory)
                    subprocess.run(["uv", "lock"], cwd=project_directory, check=True)
                    edited_files.append(os.path.join(project_directory, "uv.lock"))
                    click.echo(f"Updated uv.lock in {project_directory}")

                if (
                    project_file.endswith("pubspec.yaml")
                    and project_directory not in dart_lock_directories
                    and os.path.exists(os.path.join(project_directory, "pubspec.lock"))
                ):
                    dart_lock_directories.add(project_directory)
                    subprocess.run(["dart", "pub", "get"], cwd=project_directory, check=True)
                    edited_files.append(os.path.join(project_directory, "pubspec.lock"))
                    click.echo(f"Updated pubspec.lock in {project_directory}")

            changed_paths = sorted({file.filename for file in pr.get_files()})
            release_manifest = compute_release_manifest(
                Path("."),
                changed_paths=changed_paths,
                version=new_version,
                pr_number=pr_number,
            )
            sorted_release_targets = list(release_manifest.targets)
            print(f'release_targets: {sorted_release_targets}')

            if sorted_release_targets:
                release_string = "Release targets:\n" + "\n".join(sorted_release_targets)
            else:
                release_string = "No release targets"

            manifest_path = write_release_manifest(Path("."), release_manifest)
            repo_relative_manifest_path = os.path.relpath(manifest_path, Path.cwd())
            edited_files.append(repo_relative_manifest_path)
            click.echo(f"Updated {repo_relative_manifest_path}")

            doc_versions_path = write_doc_versions(
                Path("."),
                None,
                pending_version=new_version,
                pending_targets=sorted_release_targets,
                history_repo_root=history_repo_root,
            )
            repo_relative_doc_versions_path = os.path.relpath(doc_versions_path, Path.cwd())
            edited_files.append(repo_relative_doc_versions_path)
            click.echo(f"Updated {repo_relative_doc_versions_path}")

            commit_message = f"Bump version to {new_version} (#{pr_number})\n\n{release_string}"
            commit_sha = _commit_files_via_git_data_api(
                repo,
                pr.head.ref,
                pr.head.sha,
                edited_files,
                commit_message,
            )

    click.echo(f"Created version bump commit {commit_sha} on {pr.head.ref}")


@click.command()
@click.argument('license_header_path')
def license_header(license_header_path):
    def get_comment_syntax(file_extension, file_name):
        if file_extension in ['.py', '.sh', '.yaml', '.yml'] or file_name == 'Dockerfile' or file_name == 'Makefile':
            return '#|', ''
        elif file_extension in ['.java', '.ts', '.dart', '.js']:
            return '//|', ''
        elif file_extension in ['.html', '.svelte']:
            return '<!--|', '|-->'
        elif file_extension == '.css':
            return '/*|', '|*/'
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def read_license_header(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        header_lines = []
        for line in lines:
            if '-------------------' in line.strip():
                break
            header_lines.append(line)  # Remove trailing newlines

        # Remove final lines that are just empty strings
        while header_lines and not header_lines[-1].strip():
            header_lines.pop()

        return header_lines

    def update_file(file_path, license_header, start_comment_syntax, end_comment_syntax) -> bool:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        original_content = ''.join(lines)

        new_lines = []
        start_copying = False

        shebang = lines[0] if lines and lines[0].startswith('#!') else None

        for line in lines:
            if line.startswith('#!'):
                continue
            if start_copying:
                new_lines.append(line)
                continue
            if line.startswith(start_comment_syntax):
                continue
            if line.strip() == '':
                continue
            new_lines.append(line)
            start_copying = True

        max_length = max(len(line.strip()) for line in license_header) + 2
        license_text = ''.join([f"{start_comment_syntax}  {line.strip().ljust(max_length)}{end_comment_syntax}".strip() + "\n" for line in license_header])

        new_banner = ""

        if shebang:
            new_banner += shebang
            new_banner += "\n"

        new_banner += f"{start_comment_syntax}  {''.ljust(max_length)}{end_comment_syntax}".strip() + "\n"
        new_banner += f"{license_text.strip()}\n"
        new_banner += f"{start_comment_syntax}  {''.ljust(max_length)}{end_comment_syntax}".strip() + "\n\n"

        new_content = new_banner + ''.join(new_lines)

        if new_content == original_content:
            #print(f"Up-to-date: {file_path}")
            return False

        with open(file_path, 'w') as file:
            file.write(new_content)
        print(f"Re-written: {file_path}")

        return True

    license_header_lines = read_license_header(license_header_path)
    cli_command = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, text=True)
    files = cli_command.stdout.splitlines()

    updated_files = 0
    for file_path in files:
        if _license_header_ignored(file_path):
            continue
        if not _license_header_supported(file_path):
            continue

        file_extension = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        start_comment_syntax, end_comment_syntax = get_comment_syntax(file_extension, file_name)
        updated = update_file(file_path, license_header_lines, start_comment_syntax, end_comment_syntax)
        if updated:
            updated_files += 1

    if updated_files == 0:
        print("All files are up-to-date.")


@click.command()
def github_labels() -> None:
    PROJECT_LABEL_MAP = {
        "lib/java": "java",
        "lib/py": "py",
        "lib/ts": "ts",
        "lib/go": "go",
        "bind/dart": "dart",
        "sdk/cli": "cli",
        "sdk/console": "console",
        "sdk/prettier": "prettier"
    }

    def get_modified_files(base_branch, head_sha):
        try:
            subprocess.run(["git", "fetch", "origin", base_branch], check=True)
            result = subprocess.run(["git", "diff", "--name-only", f"origin/{base_branch}", head_sha], check=True, stdout=subprocess.PIPE)
            files = result.stdout.decode('utf-8').strip()
            return files
        except subprocess.CalledProcessError as e:
            print(f"Error fetching or diffing: {e}")
            return ""

    def get_modified_project_labels(files):
        tags = set()
        for file in files.split():
            for directory, tag in PROJECT_LABEL_MAP.items():
                if file.startswith(directory):
                    tags.add(tag)
        return tags


    # Get environment variables
    token = os.getenv('GITHUB_TOKEN')
    repository = os.getenv('GITHUB_REPOSITORY')
    pr_number_str = os.getenv('PR_NUMBER')
    if not pr_number_str:
        click.echo("PR_NUMBER environment variable not set.", err=True)
        sys.exit(1)
    pr_number = int(pr_number_str)
    base_branch = os.getenv('BASE_BRANCH')
    head_sha = os.getenv('HEAD_SHA')

    # Get modified files
    files = get_modified_files(base_branch, head_sha)
    print(f"Modified files: {files}")

    # Initialize GitHub client
    g = Github(token)
    repo = g.get_repo(repository)
    pr = repo.get_pull(pr_number)

    # Get current labels on the PR
    current_labels = {label.name for label in pr.get_labels()}

    # Determine labels to add
    new_labels = get_modified_project_labels(files)

    print(f"Labels to be added: {new_labels}")

    # Update PR labels
    added_labels = []
    removed_labels = []

    # Add new labels
    for label in new_labels:
        if label not in current_labels:
            pr.add_to_labels(label)
            added_labels.append(label)

    # Remove old labels
    for label in current_labels:
        if label not in new_labels and label in PROJECT_LABEL_MAP.values():
            pr.remove_from_labels(label)
            removed_labels.append(label)

    # Print summary
    print(f"Summary:\n  Added tags: {', '.join(added_labels) if added_labels else 'None'}\n  Removed tags: {', '.join(removed_labels) if removed_labels else 'None'}")

@click.command()
def release() -> None:
    """
    Create a GitHub release and upload assets for the specified release targets.
    """

    RELEASE_TARGET_ASSET_DIRECTORY_MAP = {
        "java": ["lib/java/target/central-publishing"],
        "py": ["lib/py/dist"],
        "ts": ["lib/ts/dist-tgz"],
        "dart": ["bind/dart/dist"],
        "cli": ["sdk/cli/dist", "sdk/cli/dist-docker"],
        "console": ["sdk/console/dist-tgz", "sdk/console/dist-docker"],
        "prettier": ["sdk/prettier/dist-tgz"]
    }

    MAX_ASSETS = 10  # Maximum number of assets to upload

    token = os.getenv('GITHUB_TOKEN')
    repository = os.getenv('GITHUB_REPOSITORY')

    if not token or not repository:
        click.echo("GITHUB_TOKEN and GITHUB_REPOSITORY environment variables must be set.")
        return

    head_commit = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE, text=True, check=True
    ).stdout.strip()

    print(f'head_commit: {head_commit}')

    manifest_file = Path(".release/release-manifest.json")
    if manifest_file.exists():
        release_manifest = load_release_manifest(Path("."))
        version = release_manifest["version"]
        pr_number = int(release_manifest["pr_number"])
        release_targets = list(release_manifest.get("targets", []))
        click.echo("Loaded release metadata from .release/release-manifest.json")
    else:
        commit_message = subprocess.run(
            ['git', 'show', '-s', '--format=%s%n%b', 'HEAD'],
            stdout=subprocess.PIPE, text=True, check=True
        ).stdout.strip()
        print(f'commit_message: {commit_message}')
        lines = commit_message.splitlines()
        legacy_info = parse_legacy_release_info(lines[0] if lines else "", "\n".join(lines[1:]))
        if legacy_info is None:
            click.echo("No release manifest found and the last commit message does not match the expected legacy format.")
            return
        version, release_targets = legacy_info
        pr_number_str = lines[0].rsplit("(#", 1)[-1].rstrip(")") if lines else ""
        pr_number = int(pr_number_str)
        click.echo("Loaded release metadata from legacy bump commit message")

    print(f'release_targets: {release_targets}')
    print(f'version: {version}')
    print(f'pr_number: {pr_number}')

    tag_name = version
    release_name = version

    g = Github(token)
    repo = g.get_repo(repository)
    pr = repo.get_pull(pr_number)

    if 'go' in release_targets:
        go_tag_version = version if version.startswith('v') else f'v{version}'
        go_module_tag = f'lib/go/{go_tag_version}'
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

    # Create the final release body
    pr_title = pr.title
    pr_url = pr.html_url
    released_projects = ''.join(f'- {target}\n' for target in release_targets) if release_targets else '(None)'
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
            target_commitish=head_commit
        )
        click.echo(f"Release created: {release.html_url}")

        # Upload assets for each release target
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
                            with open(file_path, 'rb') as asset_file:
                                release.upload_asset(
                                    path=file_path,
                                    name=file_name,
                                    label=f" [{target}]: {file_name}"
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
def verify_automerge_conditions() -> None:
    _, repo, pr, pr_number = _get_repo_and_pr()
    commenter_login = _require_env('COMMENT_AUTHOR')

    _validate_open_main_branch_pull_request(repo, pr, pr_number)

    if not repo.has_in_collaborators(commenter_login):
        raise click.ClickException(
            f"@{commenter_login} is not a collaborator on {repo.full_name}."
        )

    permission = repo.get_collaborator_permission(commenter_login)
    print(f"@{commenter_login} permission on {repo.full_name}: {permission}")
    if permission not in MERGE_ALLOWED_PERMISSION_LEVELS:
        raise click.ClickException(
            f"@{commenter_login} does not have merge permission on {repo.full_name}."
        )

    print(f"Pull request #{pr_number} is eligible for auto-merge.")


@click.command()
def tidy_pr() -> None:
    _, repo, pr, pr_number = _get_repo_and_pr()
    _validate_open_main_branch_pull_request(repo, pr, pr_number)

    if pr.draft:
        pr.mark_ready_for_review()
        print(f"Marked pull request #{pr_number} ready for review.")
        pr = _refresh_pull_request(repo, pr_number)

    comparison = repo.compare(pr.base.sha, pr.head.sha)
    if comparison.behind_by > 0:
        previous_head_sha = pr.head.sha
        pr.update_branch(expected_head_sha=previous_head_sha)
        print(f"Updated pull request #{pr_number} with {pr.base.ref}.")
        for _ in range(PR_UPDATE_BRANCH_MAX_POLLS):
            pr = _refresh_pull_request(repo, pr_number)
            if pr.head.sha != previous_head_sha:
                print(f"Pull request #{pr_number} head advanced to {pr.head.sha}.")
                break
            time.sleep(PR_UPDATE_BRANCH_POLL_INTERVAL_SECONDS)
        else:
            raise click.ClickException(
                f"Timed out waiting for pull request #{pr_number} branch update to complete."
            )
    else:
        print(f"Pull request #{pr_number} is already up to date with {pr.base.ref}.")


@click.command()
def verify_pr_requirements() -> None:
    _, repo, pr, pr_number = _get_repo_and_pr()
    _validate_open_main_branch_pull_request(repo, pr, pr_number)
    expected_head_sha = pr.head.sha

    required_contexts = list(repo.get_branch(pr.base.ref).get_required_status_checks().contexts)
    if required_contexts:
        print(f"Required status checks: {', '.join(required_contexts)}")
    else:
        print("No required status checks configured; relying on mergeability checks.")

    for attempt in range(1, PR_REQUIREMENTS_MAX_POLLS + 1):
        pr = _refresh_pull_request(repo, pr_number)
        _validate_open_main_branch_pull_request(repo, pr, pr_number)

        if pr.head.sha != expected_head_sha:
            raise click.ClickException(
                f"Pull request #{pr_number} head changed from {expected_head_sha} to {pr.head.sha} while waiting."
            )

        mergeable_state = pr.mergeable_state or "unknown"
        print(f"Attempt {attempt}: mergeable_state={mergeable_state}")

        if mergeable_state == "unknown":
            time.sleep(PR_REQUIREMENTS_POLL_INTERVAL_SECONDS)
            continue

        commit = repo.get_commit(expected_head_sha)
        check_results = _get_required_context_results_for_commit(commit)
        failed_contexts = _get_failed_required_contexts(required_contexts, check_results)
        if failed_contexts:
            raise click.ClickException(
                f"Required status checks failed for pull request #{pr_number}: {', '.join(failed_contexts)}"
            )

        pending_contexts = _get_pending_required_contexts(required_contexts, check_results)
        if pending_contexts:
            print(f"Waiting for required status checks: {', '.join(pending_contexts)}")
            time.sleep(PR_REQUIREMENTS_POLL_INTERVAL_SECONDS)
            continue

        if mergeable_state != "clean":
            raise click.ClickException(
                f"Pull request #{pr_number} does not satisfy merge requirements (mergeable_state={mergeable_state})."
            )

        print(f"Pull request #{pr_number} satisfies all merge requirements.")
        return

    raise click.ClickException(
        f"Timed out waiting for pull request #{pr_number} requirements to pass."
    )


@click.command()
def merge_pr() -> None:
    _, repo, pr, pr_number = _get_repo_and_pr()
    _validate_open_main_branch_pull_request(repo, pr, pr_number)

    merge_status = pr.merge(
        merge_method='squash',
        sha=pr.head.sha,
        delete_branch=False,
    )
    if not merge_status.merged:
        raise click.ClickException(
            f"Failed to merge pull request #{pr_number}: {merge_status.message}"
        )
    print(f"Pull request #{pr_number} merged with squash.")

@click.command()
@click.option('--add', 'add_name', help='Add a name to .gitignore')
@click.option('--remove', 'remove_name', help='Remove a name from .gitignore')
def gitignore(add_name, remove_name):
    """Add or remove entries in .gitignore"""
    if add_name and remove_name:
        raise click.UsageError("Cannot use --add and --remove at the same time.")
    if not add_name and not remove_name:
        raise click.UsageError("Must provide either --add or --remove.")

    gitignore_path = Path('.gitignore')

    if not gitignore_path.exists():
        if remove_name:
            return  # Nothing to remove
        if add_name:
            gitignore_path.touch()

    lines = gitignore_path.read_text().splitlines()
    name = add_name or remove_name

    if add_name:
        if name not in lines:
            with gitignore_path.open('a') as f:
                f.write(f"\n{name}")
    elif remove_name:
        if name in lines:
            new_lines = [line for line in lines if line != name]
            gitignore_path.write_text('\n'.join(new_lines))

main.add_command(get)
main.add_command(set_version)
main.add_command(bump)
main.add_command(license_header)
main.add_command(github_labels)
main.add_command(release)
main.add_command(publish_targets)
main.add_command(verify_automerge_conditions)
main.add_command(tidy_pr)
main.add_command(verify_pr_requirements)
main.add_command(merge_pr)
main.add_command(gitignore)
main.add_command(consolidated_readme)
main.add_command(doc_versions)

if __name__ == "__main__":
    main()
