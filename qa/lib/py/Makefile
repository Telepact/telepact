PYPROJECT = pyproject.toml
UAPI_DEP_VERSION_FILE = ../../../lib/py/VERSION.txt
CODEGEN_DEP_VERSION_FILE = ../../../tool/uapicodegen/VERSION.txt

.PHONY: all dep

all: dep $(PYPROJECT)

$(PYPROJECT): $(UAPI_DEP_VERSION_FILE) $(CODEGEN_DEP_VERSION_FILE)
	poetry run python dependency.py
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang py --out uapitest/gen --package uapitest

dep:
	cd ../../../lib/py && make
	cd ../../../tool/uapicodegen && make

