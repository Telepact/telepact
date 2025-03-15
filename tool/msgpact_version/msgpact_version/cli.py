import click
import os
from lxml import etree as ET
import json
import toml
import yaml


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
            data = yaml.safe_load(f)
        version = data["version"]
        new_version = bump_version(version)
        data["version"] = new_version
        with open("pubspec.yaml", "w") as f:
            yaml.safe_dump(data, f)
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
            data = yaml.safe_load(f)
        if "dependencies" in data and "msgpact" in data["dependencies"]:
            data["dependencies"]["msgpact"] = version
            with open("pubspec.yaml", "w") as f:
                yaml.safe_dump(data, f)
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
            data = yaml.safe_load(f)
        version = data["version"]
        click.echo(version, nl=False)
    else:
        click.echo("No supported project file found.", nl=False)


main.add_command(bump)
main.add_command(depset)
main.add_command(get)

if __name__ == "__main__":
    main()
