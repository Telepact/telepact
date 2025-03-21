.PHONY: all dep clean

all: dep
	cp ../../LICENSE ../../NOTICE telepact_cli
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf ../../lib/py/dist/*.tar.gz -C tmp
	rm -rf telepact_cli/telepact
	mv tmp/*/telepact telepact_cli/telepact
	rm -rf tmp

	rm -rf dist
	poetry lock
	poetry install
	poetry build

dep:
	cd ../../lib/py && make

clean:
	rm -rf dist
	rm -rf telepact_cli/telepact
	rm -rf tmp
	rm telepact_cli/LICENSE telepact_cli/NOTICE
	poetry env remove --all

test:
	poetry run telepact codegen --schema-dir tests/data --lang java --out tests/output/java --package output
	poetry run telepact codegen --schema-dir tests/data --lang py --out tests/output/py
	poetry run telepact codegen --schema-dir tests/data --lang ts --out tests/output/ts