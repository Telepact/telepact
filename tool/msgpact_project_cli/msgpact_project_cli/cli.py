import click
import os
import sys
from lxml import etree as ET
import json
import toml
from ruamel.yaml import YAML

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
@click.argument('directory')
def license_header(license_header_path, directory):
    print(f"license_header_path: {license_header_path}")
    print(f"directory: {directory}")

    def get_comment_syntax(file_extension):
        if file_extension in ['.py']:
            return '#'
        elif file_extension in ['.java', '.ts', '.dart']:
            return '//'
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def read_license_header(file_path):
        with open(file_path, 'r') as file:
            return file.readlines()

    def update_file(file_path, license_header, comment_syntax):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        original_content = '\n'.join(lines)

        start_license_header_index = None
        end_license_header_index = None

        header_start = '==--------------------------- MsgPact Notice ---------------------------=='
        header_end = '==---------------------------------====---------------------------------=='

        for i, line in enumerate(lines):
            if f"{comment_syntax} {header_start}" in line:
                start_license_header_index = i
            if f"{comment_syntax} {header_end}" in line:
                end_license_header_index = i
                break

        if start_license_header_index is None or end_license_header_index is None:
            return

        lines = lines[end_license_header_index + 1:]

        license_text = ''.join([f"{comment_syntax} {line}" for line in license_header])
        new_banner = f"{comment_syntax} {header_start}\n{license_text}\n{comment_syntax} {header_end}\n"

        new_content = new_banner + '\n'.join(lines)

        if new_content == original_content:
            return

        with open(file_path, 'w') as file:
            file.write(new_content)
        print(f"Updated license header in {file_path}")


    license_header = read_license_header(license_header_path)

    for root, _, files in os.walk(directory):
        for file in files:
            file_extension = os.path.splitext(file)[1]
            if file_extension in ['.py', '.java', '.ts', '.dart']:
                file_path = os.path.join(root, file)
                comment_syntax = get_comment_syntax(file_extension)
                update_file(file_path, license_header, comment_syntax)

main.add_command(bump)
main.add_command(depset)
main.add_command(get)
main.add_command(set_version)

if __name__ == "__main__":
    main()
