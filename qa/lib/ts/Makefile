BUILT_FILE = .built

.PHONY: all dep

all: dep $(BUILT_FILE)

$(BUILT_FILE):
	uapicodegen --schema-dir ../../test/schema/example --lang ts --out src/gen
	npm install
	npm run build

dep:
	cd ../../../lib/ts && make
