PYPROJECT = pyproject.toml
CODEGEN_DEP_VERSION_FILE = ../../../tool/uapicodegen/VERSION.txt

.PHONY: all dep

all: dep $(PYPROJECT)

$(PYPROJECT): $(CODEGEN_DEP_VERSION_FILE)
	poetry run python dependency.py
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang java --out src/gen/java/uapitest --package uapitest

dep:
	cd ../../../tool/uapicodegen && make

