BUILT_FILE = .built
CODEGEN_PYPROJECT = ../../../tool/uapicodegen/pyproject.toml

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE): $(CODEGEN_PYPROJECT)
	cp ../../../lib/ts/dist/*.tar.gz uapi.tar.gz
	uapicodegen --schema-dir ../../test/schema/example --lang ts --out src/gen
	npm install
	npm run build

dep:
	cd ../../../lib/ts && make
