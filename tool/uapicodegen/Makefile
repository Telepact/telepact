PYPROJECT = pyproject.toml
SRC_FILES = $(shell find uapicodegen -name '*.py' -o -name '*.toml' -o -name '*.j2')
DEP_VERSION_FILE = ../../lib/py/VERSION.txt
UAPI_PYPROJECT = ../../lib/py/pyproject.toml

.PHONY: all dep

all: dep $(PYPROJECT)

${PYPROJECT}: $(SRC_FILES) $(UAPI_PYPROJECT)
	@uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)

dep:
	cd ../../lib/py && make