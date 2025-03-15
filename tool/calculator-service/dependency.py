import toml


def update_versions(pyproject_path: str, msgpact_version_path: str) -> None:
    with open(msgpact_version_path, 'r') as file:
        msgpact_version = file.read().strip()

    with open(pyproject_path, 'r') as file:
        pyproject_data = toml.load(file)

    pyproject_data['tool']['poetry']['dependencies']['msgpact'][
        'path'] = f"../../lib/py/dist/msgpact-{msgpact_version}-py3-none-any.whl"

    with open(pyproject_path, 'w') as file:
        toml.dump(pyproject_data, file)


if __name__ == "__main__":
    update_versions('pyproject.toml', '../../lib/py/VERSION.txt')
