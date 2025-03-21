import click
import os
import sys
from lxml import etree as ET
import json
import toml
from ruamel.yaml import YAML
import subprocess

yaml = YAML()

def bump_version(version: str) -> str:
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"


@click.group()
def main() -> None:
    pass


@click.command()
def bump() -> None:
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
            if artifact_id == "msgpact":
                dependency.find(
                    "{http://maven.apache.org/POM/4.0.0}version").text = version
                break
        tree.write("pom.xml", xml_declaration=True,
                   encoding='utf-8', pretty_print=True)
        click.echo(f"Set msgpact dependency to version {version} in pom.xml")
    elif os.path.exists("package.json"):
        with open("package.json", "r") as f:
            data = json.load(f)
        if "dependencies" in data and "msgpact" in data["dependencies"]:
            data["dependencies"]["msgpact"] = version
            with open("package.json", "w") as f:
                json.dump(data, f, indent=2)
            click.echo(
                f"Set msgpact dependency to version {version} in package.json")
        else:
            click.echo("msgpact dependency not found in package.json")
    elif os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
        if "dependencies" in data["project"] and "msgpact" in data["project"]["dependencies"]:
            data["project"]["dependencies"]["msgpact"] = version
            with open("pyproject.toml", "w") as f:
                toml.dump(data, f)
            click.echo(
                f"Set msgpact dependency to version {version} in pyproject.toml")
        else:
            click.echo("msgpact dependency not found in pyproject.toml")
    elif os.path.exists("pubspec.yaml"):
        with open("pubspec.yaml", "r") as f:
            data = yaml.load(f)
        if "dependencies" in data and "msgpact" in data["dependencies"]:
            data["dependencies"]["msgpact"] = version
            with open("pubspec.yaml", "w") as f:
                yaml.dump(data, f)
            click.echo(
                f"Set msgpact dependency to version {version} in pubspec.yaml")
        else:
            click.echo("msgpact dependency not found in pubspec.yaml")
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
@click.argument('license_header_path')
def license_header(license_header_path):
    def get_comment_syntax(file_extension, file_name):
        if file_extension in ['.py', '.sh', '.yaml', '.yml'] or file_name == 'Dockerfile' or file_name == 'Makefile':
            return '#', ''
        elif file_extension in ['.java', '.ts', '.dart', '.js']:
            return '//', ''
        elif file_extension in ['.html', '.svelte']:
            return '<!--', '-->'
        elif file_extension == '.css':
            return '/*', '*/'
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def read_license_header(file_path):
        with open(file_path, 'r') as file:
            return file.readlines()

    def update_file(file_path, license_header, start_comment_syntax, end_comment_syntax):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        original_content = ''.join(lines)

        first_non_header_index = None

        for i, line in enumerate(lines):
            if line.startswith(f"{start_comment_syntax}|"):
                first_non_header_index = i
                continue
            break

        if first_non_header_index is not None:
            lines = lines[(first_non_header_index + 1) + 1:]

        max_length = max(len(line.strip()) for line in license_header) + 1
        license_text = ''.join([f"{start_comment_syntax}|  {line.strip().ljust(max_length)}{end_comment_syntax}\n" for line in license_header])

        new_banner = ""
        new_banner += f"{start_comment_syntax}|" + f"{''.ljust(max_length)}" if end_comment_syntax else '' + f"{end_comment_syntax}\n"
        new_banner += f"{license_text.strip()}\n"
        new_banner += f"{start_comment_syntax}|" + f"{''.ljust(max_length)}" if end_comment_syntax else '' + f"{end_comment_syntax}\n\n"

        new_content = new_banner + ''.join(lines)

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

main.add_command(bump)
main.add_command(depset)
main.add_command(get)
main.add_command(set_version)
main.add_command(license_header)

if __name__ == "__main__":
    main()
