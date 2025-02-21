UAPI_PYPROJECT = ../../../lib/py/pyproject.toml
CODEGEN_PYPROJECT = ../../../tool/uapicodegen/pyproject.toml
BUILT_FILE=.built

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(UAPI_PYPROJECT) $(CODEGEN_PYPROJECT)
	cp ../../../lib/py/dist/*.tar.gz uapi.tar.gz
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang py --out uapitest/gen --package uapitest

dep:
	cd ../../../lib/py && make
	cd ../../../tool/uapicodegen && make

