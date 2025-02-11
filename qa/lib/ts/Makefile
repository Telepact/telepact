BUILT_FILE = .built
CODEGEN_PYPROJECT = ../../../tool/uapicodegen/pyproject.toml

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(CODEGEN_PYPROJECT)
	poetry lock
	poetry install
	poetry run python -m uapicodegen --schema-dir ../../test/schema/example --lang ts --out src/gen --package uapitest
	@touch $(BUILT_FILE)

dep:
	@cd ../../../tool/uapicodegen && make

