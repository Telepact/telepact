import toml

def update_versions(pyproject_path, uapi_version_path, codegen_version_path):
    with open(uapi_version_path, 'r') as file:
        uapi_version = file.read().strip()
    
    with open(codegen_version_path, 'r') as file:
        codegen_version = file.read().strip()
    
    with open(pyproject_path, 'r') as file:
        pyproject_data = toml.load(file)
    
    pyproject_data['tool']['poetry']['dependencies']['uapicodegen']['path'] = f"./../../../tool/uapicodegen/dist/uapicodegen-{codegen_version}-py3-none-any.whl"
    pyproject_data['tool']['poetry']['dependencies']['uapi']['path'] = f"../../../lib/py/dist/uapi-{uapi_version}-py3-none-any.whl"
    
    with open(pyproject_path, 'w') as file:
        toml.dump(pyproject_data, file)

if __name__ == "__main__":
    update_versions('pyproject.toml', '../../../lib/py/VERSION.txt', '../../../tool/uapicodegen/VERSION.txt')
