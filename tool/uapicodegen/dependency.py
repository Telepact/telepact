import toml

def update_uapi_version():
    version_file_path = '../../lib/py/VERSION.txt'
    pyproject_file_path = 'pyproject.toml'
    
    with open(version_file_path, 'r') as version_file:
        uapi_version = version_file.read().strip()
    
    pyproject_data = toml.load(pyproject_file_path)
    
    dependencies = pyproject_data['project']['dependencies']
    for i, dep in enumerate(dependencies):
        if dep.startswith('uapi @'):
            dependencies[i] = f'uapi @ file:///Users/brendanbartels/workspace/jAPI/lib/py/dist/uapi-{uapi_version}-py3-none-any.whl'
    
    pyproject_data['project']['dependencies'] = dependencies
    
    with open(pyproject_file_path, 'w') as pyproject_file:
        toml.dump(pyproject_data, pyproject_file)

# Call the function to update the version
update_uapi_version()