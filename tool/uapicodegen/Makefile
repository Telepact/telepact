PYPROJECT = pyproject.toml
SRC_FILES = $(shell find uapicodegen -name '*.py' -o -name '*.toml' -o -name '*.j2')
DEP_VERSION_FILE = ../../lib/py/VERSION.txt
UAPI_PYPROJECT = ../../lib/py/pyproject.toml

.PHONY: all dep

all: dep $(PYPROJECT)

${PYPROJECT}: $(SRC_FILES) $(UAPI_PYPROJECT)
	@bump-patch-version || (echo "Install bump-patch-version with 'pipx install ../../tool/bump_patch_version'" && exit 1)

dep:
	cd ../../lib/py && make