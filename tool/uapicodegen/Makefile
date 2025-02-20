PYPROJECT = pyproject.toml
SRC_FILES = $(shell find uapicodegen -name '*.py' -o -name '*.toml' -o -name '*.j2')
UAPI_PYPROJECT = ../../lib/py/pyproject.toml

.PHONY: all dep

all: dep $(PYPROJECT)
	cp ../../LICENSE ../../NOTICE uapicodegen
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf ../../lib/py/dist/*.tar.gz -C tmp
	rm -rf uapicodegen/uapi
	mv tmp/*/uapi uapicodegen/uapi

	poetry install
	poetry build

	

${PYPROJECT}: $(SRC_FILES) $(UAPI_PYPROJECT)
	@uapi-version bump || (echo "Install uapi-version bump with 'pipx install ../../tool/uapi_version'" && exit 1)

dep:
	cd ../../lib/py && make