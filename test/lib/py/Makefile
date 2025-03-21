.PHONY: all dep

all: dep
	cp ../../../lib/py/dist/*.tar.gz telepact.tar.gz

	poetry lock
	poetry remove telepact || echo "no-op"
	poetry add ./telepact.tar.gz
	poetry install

	telepact codegen --schema-dir ../../runner/schema/example --lang py --out telepact_test/gen


dep:
	cd ../../../lib/py && make

