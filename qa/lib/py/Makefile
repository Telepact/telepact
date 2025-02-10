BUILT = .built
UAPI_DEP_VERSION_FILE = ../../../lib/py/pyproject.toml
CODEGEN_DEP_VERSION_FILE = ../../../tool/uapicodegen/VERSION.txt

.PHONY: all dep

all: dep $(BUILT)

$(BUILT): $(UAPI_DEP_VERSION_FILE) $(CODEGEN_DEP_VERSION_FILE)
	poetry lock
	poetry install
#	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang py --out uapitest/gen --package uapitest

dep:
	cd ../../../lib/py && make
	cd ../../../tool/uapicodegen && make

