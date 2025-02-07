import toml


def update_versions(pyproject_path: str, codegen_version_path: str) -> None:
    with open(codegen_version_path, 'r') as file:
        codegen_version = file.read().strip()

    with open(pyproject_path, 'r') as file:
        pyproject_data = toml.load(file)

    pyproject_data['tool']['poetry']['dependencies']['uapicodegen'][
        'path'] = f"./../../../tool/uapicodegen"

    with open(pyproject_path, 'w') as file:
        toml.dump(pyproject_data, file)


if __name__ == "__main__":
    update_versions('pyproject.toml', '../../../tool/uapicodegen/VERSION.txt')
