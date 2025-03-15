.PHONY: all dep

all: dep
	cp ../../../lib/py/dist/*.tar.gz msgpact.tar.gz

	poetry lock
	poetry remove msgpact || echo "no-op"
	poetry add ./msgpact.tar.gz
	poetry install

	msgpact-codegen --schema-dir ../../test/schema/example --lang py --out msgpact_test/gen


dep:
	cd ../../../lib/py && make

