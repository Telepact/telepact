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
from github import Github

yaml = YAML()

def bump_version(version: str) -> str:
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"


@click.group()
def main() -> None:
    pass


@click.command()
def old_bump() -> None:
    if os.path.exists("pom.xml"):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse("pom.xml", parser)
        root = tree.getroot()
        version = root.find("{http://maven.apache.org/POM/4.0.0}version").text
        new_version = bump_version(version)
        root.find(
            "{http://maven.apache.org/POM/4.0.0}version").text = new_version
        tree.write("pom.xml", xml_declaration=True,
                   encoding='utf-8', pretty_print=True)
        click.echo(f"Updated pom.xml to version {new_version}")
    elif os.path.exists("package.json"):
        with open("package.json", "r") as f:
            data = json.load(f)
        version = data["version"]
        new_version = bump_version(version)
        data["version"] = new_version
        with open("package.json", "w") as f:
            json.dump(data, f, indent=2)
        click.echo(f"Updated package.json to version {new_version}")
    elif os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        version = data["project"]["version"]
        new_version = bump_version(version)
        data["project"]["version"] = new_version
        with open("pyproject.toml", "w") as f:
            toml.dump(data, f)
        click.echo(f"Updated pyproject.toml to version {new_version}")
    elif os.path.exists("pubspec.yaml"):
        with open("pubspec.yaml", "r") as f:
            data = yaml.load(f)
        version = data["version"]
        new_version = bump_version(version)
        data["version"] = new_version
        with open("pubspec.yaml", "w") as f:
            yaml.dump(data, f)
        click.echo(f"Updated pubspec.yaml to version {new_version}")
    else:
        click.echo("No supported project file found.")


@click.command()
@click.argument('version')
def depset(version: str) -> None:
    if os.path.exists("pom.xml"):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse("pom.xml", parser)
        root = tree.getroot()
        dependencies = root.find(
            "{http://maven.apache.org/POM/4.0.0}dependencies")
        for dependency in dependencies.findall("{http://maven.apache.org/POM/4.0.0}dependency"):
            artifact_id = dependency.find(
                "{http://maven.apache.org/POM/4.0.0}artifactId").text
            if artifact_id == "telepact":
                dependency.find(
                    "{http://maven.apache.org/POM/4.0.0}version").text = version
                break
        tree.write("pom.xml", xml_declaration=True,
                   encoding='utf-8', pretty_print=True)
        click.echo(f"Set telepact dependency to version {version} in pom.xml")
    elif os.path.exists("package.json"):
        with open("package.json", "r") as f:
            data = json.load(f)
        if "dependencies" in data and "telepact" in data["dependencies"]:
            data["dependencies"]["telepact"] = version
            with open("package.json", "w") as f:
                json.dump(data, f, indent=2)
            click.echo(
                f"Set telepact dependency to version {version} in package.json")
        else:
            click.echo("telepact dependency not found in package.json")
    elif os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        if "dependencies" in data["project"] and "telepact" in data["project"]["dependencies"]:
            data["project"]["dependencies"]["telepact"] = version
            with open("pyproject.toml", "w") as f:
                toml.dump(data, f)
            click.echo(
                f"Set telepact dependency to version {version} in pyproject.toml")
        else:
            click.echo("telepact dependency not found in pyproject.toml")
    elif os.path.exists("pubspec.yaml"):
        with open("pubspec.yaml", "r") as f:
            data = yaml.load(f)
        if "dependencies" in data and "telepact" in data["dependencies"]:
            data["dependencies"]["telepact"] = version
            with open("pubspec.yaml", "w") as f:
                yaml.dump(data, f)
            click.echo(
                f"Set telepact dependency to version {version} in pubspec.yaml")
        else:
            click.echo("telepact dependency not found in pubspec.yaml")
    else:
        click.echo("No supported project file found.")


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
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        version = data["project"]["version"]
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
        with open("package.json", "w") as f:
            json.dump(data, f, indent=2)
        click.echo(f"Set package.json to version {version}")
        updated = True

    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        data["project"]["version"] = version
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

    pr_number = int(os.getenv('PR_NUMBER'))

    # Get the paths from the previous commit
    prev_commit_paths = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=format:', 'HEAD'],
        stdout=subprocess.PIPE, text=True
    ).stdout.strip().split('\n')

    print('prev_commit_paths:')
    print(prev_commit_paths)

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
                with open(project_file, 'w') as f:
                    json.dump(data, f, indent=2)
                click.echo(f"Updated {project_file} to version {new_version}")
                edited_files.append(project_file)
            elif project_file.endswith("pyproject.toml"):
                with open(project_file, 'r') as f:
                    data = toml.load(f)
                data["project"]["version"] = new_version
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

        if project_file.endswith("pyproject.toml") and os.path.exists(os.path.join(os.path.dirname(project_file), "poetry.lock")):
            subprocess.run(["poetry", "lock"], cwd=os.path.dirname(project_file), check=True)
            edited_files.append(os.path.join(os.path.dirname(project_file), "poetry.lock"))
            click.echo(f"Updated poetry.lock in {os.path.dirname(project_file)}")

        if project_file.endswith("pubspec.yaml") and os.path.exists(os.path.join(os.path.dirname(project_file), "pubspec.lock")):
            subprocess.run(["dart", "pub", "get"], cwd=os.path.dirname(project_file), check=True)
            edited_files.append(os.path.join(os.path.dirname(project_file), "pubspec.lock"))
            click.echo(f"Updated pubspec.lock in {os.path.dirname(project_file)}")

    # Determine release targets based on the paths
    release_targets = set()
    for path in prev_commit_paths:
        if 'lib/java' in path:
            release_targets.add('java')
        if 'lib/py' in path:
            release_targets.add('py')
        if 'lib/ts' in path:
            release_targets.add('ts')
        if 'bind/dart' in path:
            release_targets.add('dart')
        if 'sdk/cli' in path:
            release_targets.add('cli')
        if 'sdk/console' in path:
            release_targets.add('console')
        if 'sdk/docker' in path:
            release_targets.add('docker')
        if 'sdk/prettier' in path:
            release_targets.add('prettier')

    print(f'release_targets: {release_targets}')

    if release_targets:
        release_string = "Release targets:\n" + "\n".join(release_targets)
    else:
        release_string = "No release targets"

    # Create the new commit message
    new_commit_msg = f"Bump version to {new_version} (#{pr_number})\n\n" + release_string

    # Add and commit the changes
    subprocess.run(['git', 'add'] + edited_files)
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

    def update_file(file_path, license_header, start_comment_syntax, end_comment_syntax):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        original_content = ''.join(lines)

        new_lines = []
        start_copying = False

        for line in lines:
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
        new_banner += f"{start_comment_syntax}  {''.ljust(max_length)}{end_comment_syntax}".strip() + "\n"
        new_banner += f"{license_text.strip()}\n"
        new_banner += f"{start_comment_syntax}  {''.ljust(max_length)}{end_comment_syntax}".strip() + "\n\n"

        new_content = new_banner + ''.join(new_lines)

        if new_content == original_content:
            print(f"Up-to-date: {file_path}")
            return

        with open(file_path, 'w') as file:
            file.write(new_content)
        print(f"Re-written: {file_path}")

    cli_command = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, text=True)
    files = cli_command.stdout.splitlines()

    for file_path in files:
        license_header = read_license_header(license_header_path)
        file_extension = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        if file_name != 'pubspec.yaml' and file_extension in ['.py', '.java', '.ts', '.dart', '.sh', '.js', '.yaml', '.yml', '.html', '.css', '.svelte'] or file_name == 'Dockerfile' or file_name == 'Makefile':
            start_comment_syntax, end_comment_syntax = get_comment_syntax(file_extension, file_name)
            update_file(file_path, license_header, start_comment_syntax, end_comment_syntax)
        else:
            print(f"ERROR: {file_path} - Unsupported file extension {file_extension}")

@click.command()
def github_labels() -> None:
    # Directories and their corresponding tags
    DIRECTORY_TAG_MAP = {
        "lib/java": "java",
        "lib/py": "py",
        "lib/ts": "ts",
        "bind/dart": "dart",
        "sdk/cli": "cli",
        "sdk/console": "console",
        "sdk/docker": "docker",
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

    def get_modified_tags(files):
        tags = set()
        for file in files.split():
            for directory, tag in DIRECTORY_TAG_MAP.items():
                if file.startswith(directory):
                    tags.add(tag)
        return tags


    # Get environment variables
    token = os.getenv('GITHUB_TOKEN')
    repository = os.getenv('GITHUB_REPOSITORY')
    pr_number = int(os.getenv('PR_NUMBER'))
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

    # Determine tags to add
    new_tags = get_modified_tags(files)
    print(f"Tags to be added: {new_tags}")

    # Update PR labels
    added_tags = []
    removed_tags = []

    # Add new labels
    for tag in new_tags:
        if tag not in current_labels:
            pr.add_to_labels(tag)
            added_tags.append(tag)

    # Remove old labels
    for label in current_labels:
        if label not in new_tags and label in DIRECTORY_TAG_MAP.values():
            pr.remove_from_labels(label)
            removed_tags.append(label)

    # Print summary
    print(f"Summary:\n  Added tags: {', '.join(added_tags) if added_tags else 'None'}\n  Removed tags: {', '.join(removed_tags) if removed_tags else 'None'}")

@click.command()
def release() -> None:
    """
    Create a GitHub release and upload assets for the specified release targets.
    """

    RELEASE_TARGET_ASSET_DIRECTORY_MAP = {
        "java": "lib/java/target/central-publishing",
        "py": "lib/py/dist",
        "ts": "lib/ts/dist-tgz",
        "dart": "bind/dart/dist",
        "cli": "sdk/cli/dist",
        "console": "sdk/console/dist",
        "docker": "sdk/docker/dist",
        "prettier": "sdk/prettier/dist-tgz"
    }

    MAX_ASSETS = 10  # Maximum number of assets to upload

    token = os.getenv('GITHUB_TOKEN')
    repository = os.getenv('GITHUB_REPOSITORY')

    if not token or not repository:
        click.echo("GITHUB_TOKEN and GITHUB_REPOSITORY environment variables must be set.")
        return

    # Extract version string and release targets from the last git commit message
    commit_message = subprocess.run(
        ['git', 'show', '-s', '--format=%s%n%b', 'HEAD'],
        stdout=subprocess.PIPE, text=True, check=True
    ).stdout.strip()

    head_commit = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE, text=True, check=True
    ).stdout.strip()

    print(f'commit_message: {commit_message}')
    print(f'head_commit: {head_commit}')

    lines = commit_message.splitlines()
    if not lines[0].startswith("Bump version to"):
        click.echo("The last commit message does not match the expected format.")
        return
    version = lines[0].split(" ")[3]

    if len(lines) > 2 and lines[2] == 'Release targets:':
        release_targets = lines[3:]
    else:
        release_targets = []

    print(f'release_targets: {release_targets}')

    tag_name = version
    release_name = version
    final_release_body = f"### Release Targets:\n\n{release_targets}".strip()

    g = Github(token)
    repo = g.get_repo(repository)

    try:
        release = repo.create_git_release(
            tag=tag_name,
            name=release_name,
            message=final_release_body,
            draft=True,
            prerelease=True,
            target_commitish=head_commit
        )
        click.echo(f"Release created: {release.html_url}")

        # Upload assets for each release target
        asset_count = 0
        for target in release_targets:
            asset_directory = RELEASE_TARGET_ASSET_DIRECTORY_MAP.get(target)
            if asset_directory and os.path.exists(asset_directory):
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
                                label=f"{target} - {file_name}"
                            )
                            asset_count += 1
                            click.echo(f"Uploaded asset: {file_name} for target: {target}")
            else:
                click.echo(f"No assets found for target: {target} in directory: {asset_directory}")

    except Exception as e:
        click.echo(f"Failed to create release or upload assets: {e}")

main.add_command(old_bump)
main.add_command(depset)
main.add_command(get)
main.add_command(set_version)
main.add_command(bump)
main.add_command(license_header)
main.add_command(github_labels)
main.add_command(release)

if __name__ == "__main__":
    main()
