# Bump Patch Version CLI

This CLI tool bumps the patch version of a project based on the presence of `pom.xml`, `package.json`, or `pyproject.toml` in the current directory.

## Installation

First, ensure you have [Poetry](https://python-poetry.org/) installed. Then, install the dependencies and build the project:

```sh
poetry install
```

## Usage

To bump the patch version, navigate to the directory containing your project file (`pom.xml`, `package.json`, or `pyproject.toml`) and run:

```sh
bump-patch-version
```

The CLI will automatically detect the project file and update the patch version.

## Example

```sh
cd /path/to/your/project
bump-patch-version
```

This will update the patch version in the detected project file and print a message indicating the new version.
