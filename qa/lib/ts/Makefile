BUILT = .built
CODEGEN_DEP_VERSION_FILE = ../../../tool/uapicodegen/VERSION.txt

.PHONY: all dep

all: dep $(BUILT)

$(BUILT): $(CODEGEN_DEP_VERSION_FILE)
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang ts --out src/gen --package uapitest

dep:
	cd ../../../tool/uapicodegen && make

