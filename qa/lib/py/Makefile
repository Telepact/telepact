UAPI_PYPROJECT = ../../../lib/py/pyproject.toml
BUILT_FILE=.built

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(UAPI_PYPROJECT)
	cp ../../../lib/py/dist/*.tar.gz uapi.tar.gz

	poetry lock
	poetry install

	uapicodegen --schema-dir ../../test/schema/example --lang py --out uapitest/gen


dep:
	cd ../../../lib/py && make

