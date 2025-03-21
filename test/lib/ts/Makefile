.PHONY: all dep

all: dep
	telepact codegen --schema-dir ../../runner/schema/example --lang ts --out src/gen
	npm install
	npm run build

dep:
	cd ../../../lib/ts && make
