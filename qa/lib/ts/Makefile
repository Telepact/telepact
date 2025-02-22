BUILT_FILE = .built
CODEGEN_PYPROJECT = ../../../tool/uapicodegen/pyproject.toml

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(CODEGEN_PYPROJECT)
	uapicodegen --schema-dir ../../test/schema/example --lang ts --out src/gen
	npm install
	npm run build

dep:
	cd ../../../lib/ts && make
