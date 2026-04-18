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
import os
import sys
from lxml import etree as ET
import json
import toml
from ruamel.yaml import YAML
import subprocess
from github import Github, GithubException
from pathlib import Path

from .commands.consolidated_readme import consolidated_readme
from .commands.doc_versions import doc_versions, write_doc_versions
from .release_plan import (
    changed_paths_for_commits,
    compute_release_manifest,
    load_release_manifest,
    release_commits_since_last_bump,
    resolve_publish_targets,
    write_release_manifest,
)

yaml = YAML()
LICENSE_HEADER_IGNORE_FILE = ".license-header-ignore"


def _write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2) + "\n")


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
    version_file = 'VERSION.txt'

    project_files = [
        'lib/java/pom.xml',
        'lib/py/pyproject.toml',
        'lib/ts/package.json',
        'bind/dart/pubspec.yaml',
        'bind/dart/package.json',
        'sdk/cli/pyproject.toml',
        'sdk/prettier/package.json',
        'sdk/console/package.json',
    ]

    def bump_version2(version: str) -> str:
        parts = version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts)

    if not os.path.exists(version_file):
        click.echo(f"Version file {version_file} does not exist.")
        return

    with open(version_file, 'r') as f:
        version = f.read().strip()

    new_version = bump_version2(version)

    with open(version_file, 'w') as f:
        f.write(new_version)

    click.echo(f"Updated version file {version_file} to version {new_version}")

    edited_files = [version_file]

    for project_file in project_files:
        if os.path.exists(project_file):
            if project_file.endswith("pom.xml"):
                parser = ET.XMLParser(remove_blank_text=True)
                tree = ET.parse(project_file, parser)
                root = tree.getroot()
                root.find("{http://maven.apache.org/POM/4.0.0}version").text = new_version
                tree.write(project_file, xml_declaration=True, encoding='utf-8', pretty_print=True)
                click.echo(f"Updated {project_file} to version {new_version}")
                edited_files.append(project_file)
            elif project_file.endswith("package.json"):
                with open(project_file, 'r') as f:
                    data = json.load(f)
                data["version"] = new_version
                _write_json(project_file, data)
                click.echo(f"Updated {project_file} to version {new_version}")
                edited_files.append(project_file)
            elif project_file.endswith("pyproject.toml"):
                with open(project_file, 'r') as f:
                    data = toml.load(f)
                data = _set_project_version(data, new_version)
                with open(project_file, 'w') as f:
                    toml.dump(data, f)
                click.echo(f"Updated {project_file} to version {new_version}")
                edited_files.append(project_file)
            elif project_file.endswith("pubspec.yaml"):
                with open(project_file, 'r') as f:
                    data = yaml.load(f)
                data["version"] = new_version
                with open(project_file, 'w') as f:
                    yaml.dump(data, f)
                click.echo(f"Updated {project_file} to version {new_version}")
                edited_files.append(project_file)
            else:
                click.echo(f"Unsupported project file type: {project_file}")
        else:
            click.echo(f"Project file {project_file} does not exist.")

    # Update lock files
    for project_file in project_files:
        if project_file.endswith("package.json") and os.path.exists(os.path.join(os.path.dirname(project_file), "package-lock.json")):
            subprocess.run(["npm", "install"], cwd=os.path.dirname(project_file), check=True)
            edited_files.append(os.path.join(os.path.dirname(project_file), "package-lock.json"))
            click.echo(f"Updated package-lock.json in {os.path.dirname(project_file)}")

        if project_file.endswith("pyproject.toml") and os.path.exists(os.path.join(os.path.dirname(project_file), "uv.lock")):
            subprocess.run(["uv", "lock"], cwd=os.path.dirname(project_file), check=True)
            edited_files.append(os.path.join(os.path.dirname(project_file), "uv.lock"))
            click.echo(f"Updated uv.lock in {os.path.dirname(project_file)}")

        if project_file.endswith("pubspec.yaml") and os.path.exists(os.path.join(os.path.dirname(project_file), "pubspec.lock")):
            subprocess.run(["dart", "pub", "get"], cwd=os.path.dirname(project_file), check=True)
            edited_files.append(os.path.join(os.path.dirname(project_file), "pubspec.lock"))
            click.echo(f"Updated pubspec.lock in {os.path.dirname(project_file)}")

    included_commits = release_commits_since_last_bump(Path("."))
    changed_paths = changed_paths_for_commits(Path("."), included_commits)

    release_manifest = compute_release_manifest(
        Path("."),
        changed_paths=changed_paths,
        version=new_version,
        included_commits=included_commits,
    )
    sorted_release_targets = list(release_manifest.targets)

    manifest_path = write_release_manifest(Path("."), release_manifest)
    repo_relative_manifest_path = os.path.relpath(manifest_path, Path.cwd())
    edited_files.append(repo_relative_manifest_path)
    click.echo(f"Updated {repo_relative_manifest_path}")

    doc_versions_path = write_doc_versions(
        Path("."),
        None,
        pending_version=new_version,
        pending_targets=sorted_release_targets,
    )
    repo_relative_doc_versions_path = os.path.relpath(doc_versions_path, Path.cwd())
    edited_files.append(repo_relative_doc_versions_path)
    click.echo(f"Updated {repo_relative_doc_versions_path}")

    new_commit_msg = f"Bump version to {new_version}"

    subprocess.run(['git', 'add'] + list(dict.fromkeys(edited_files)))
    subprocess.run(['git', 'commit', '-m', new_commit_msg])


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

    release_manifest = load_release_manifest(Path("."))
    version = release_manifest["version"]
    release_targets = list(release_manifest.get("targets", []))
    included_commits = list(release_manifest.get("included_commits", []))
    click.echo("Loaded release metadata from .release/release-manifest.json")

    tag_name = version
    release_name = version

    g = Github(token)
    repo = g.get_repo(repository)

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

    included_prs = [f"- {subject}" for subject in included_commits if isinstance(subject, str) and subject.strip()]
    included_prs_string = "\n".join(included_prs) if included_prs else "(None)"

    released_projects = ''.join(f'- {target}\n' for target in release_targets) if release_targets else '(None)'
    final_release_body = (
        f"### Included Commits\n"
        f"{included_prs_string}\n\n"
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
@click.option("--github-output", default=None, type=click.Path(dir_okay=False, path_type=Path), help="Write key=value lines for GitHub Actions outputs.")
def publish_targets(release_tag: str | None, github_output: Path | None) -> None:
    outputs = resolve_publish_targets(
        Path("."),
        release_tag=release_tag,
    )

    lines = [f"{key}={'true' if value else 'false'}" for key, value in outputs.items()]
    if github_output is not None:
        github_output.parent.mkdir(parents=True, exist_ok=True)
        github_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        click.echo("\n".join(lines))

@click.command()
@click.option("--title", required=True, help="Pull request title.")
@click.option("--body", default="", help="Pull request body.")
@click.option("--head", required=True, help="Head branch name.")
@click.option("--base", required=True, help="Base branch name.")
@click.option("--draft/--no-draft", default=False, help="Create the pull request as a draft.")
@click.option(
    "--maintainer-can-modify/--no-maintainer-can-modify",
    default=False,
    help="Allow maintainers to modify the pull request branch.",
)
def create_pull_request(
    title: str,
    body: str,
    head: str,
    base: str,
    draft: bool,
    maintainer_can_modify: bool,
) -> None:
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")

    if not github_token:
        raise click.ClickException("GITHUB_TOKEN environment variable is not set.")
    if not github_repository:
        raise click.ClickException("GITHUB_REPOSITORY environment variable is not set (e.g., 'owner/repo').")

    github = Github(github_token)
    repo = github.get_repo(github_repository)
    pull_request = repo.create_pull(
        title=title,
        body=body,
        head=head,
        base=base,
        draft=draft,
        maintainer_can_modify=maintainer_can_modify,
    )

    click.echo(f"Created pull request #{pull_request.number}: {pull_request.html_url}")


@click.command()
def automerge():
    """
    Approves and squashes a Pull Request if the author is on the hardcoded allow list.
    All necessary information is retrieved from environment variables.
    """

    AUTOMERGE_ALLOWED_AUTHORS = ["dependabot[bot]", "telepact-notary[bot]"]

    AUTOMERGE_ALLOWED_FILES = [
        ".release/release-manifest.json",
        "bind/dart/package-lock.json",
        "bind/dart/package.json",
        "bind/dart/pubspec.lock",
        "bind/dart/pubspec.yaml",
        "VERSION.txt",
        "doc/04-operate/03-versions.md",
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
        "tool/telepact_project_cli/pyproject.toml"
    ]

    pr_number_str = os.getenv('PR_NUMBER')
    github_token = os.getenv('GITHUB_TOKEN')
    github_repository = os.getenv('GITHUB_REPOSITORY')

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
        if f.status == 'removed':
            raise Exception(f"Pull Request #{pr_number} contains removed files. Aborting automerge.")
        if f.filename not in AUTOMERGE_ALLOWED_FILES:
            raise Exception(f"Pull Request #{pr_number} contains changes in the file '{f.filename}' which is not allowed for automerge.")

    print("Approving Pull Request...")
    pr.create_review(event='APPROVE')
    print("Pull Request approved.")

    pr.enable_automerge(merge_method='SQUASH')
    print("Pull Request will be automerged when build succeeds.")

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
main.add_command(create_pull_request)
main.add_command(automerge)
main.add_command(gitignore)
main.add_command(consolidated_readme)
main.add_command(doc_versions)

if __name__ == "__main__":
    main()
