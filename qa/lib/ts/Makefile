.PHONY: all dep

all: dep
	msgpact codegen --schema-dir ../../test/schema/example --lang ts --out src/gen
	npm install
	npm run build

dep:
	cd ../../../lib/ts && make
