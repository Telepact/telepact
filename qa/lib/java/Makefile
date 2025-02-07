BUILT = .built
CODEGEN_DEP_VERSION_FILE = ../../../tool/uapicodegen/VERSION.txt

.PHONY: all dep

all: dep $(BUILT)

$(BUILT): $(CODEGEN_DEP_VERSION_FILE)
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang java --out src/gen/java/uapitest --package uapitest
	touch $(BUILT)

dep:
	cd ../../../tool/uapicodegen && make

