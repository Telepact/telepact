import toml

# Increment the patch version of this library in the pyproject.toml file
def increment_patch_version(pyproject_path: str):
    with open(pyproject_path, 'r') as file:
        pyproject_data = toml.load(file)
    
    version = pyproject_data['project']['version']
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    pyproject_data['project']['version'] = new_version
    
    with open(pyproject_path, 'w') as file:
        toml.dump(pyproject_data, file)

    # Write new_version to a file named VERSION.txt
    with open('VERSION.txt', 'w') as version_file:
        version_file.write(new_version)
    
    print(f"Version incremented to {new_version}")

increment_patch_version('pyproject.toml')
