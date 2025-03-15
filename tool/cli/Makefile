.PHONY: all dep clean

all: dep
	cp ../../LICENSE ../../NOTICE msgpact_cli
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf ../../lib/py/dist/*.tar.gz -C tmp
	rm -rf msgpact_cli/msgpact
	mv tmp/*/msgpact msgpact_cli/msgpact
	rm -rf tmp

	rm -rf dist
	poetry lock
	poetry install
	poetry build

dep:
	cd ../../lib/py && make

clean:
	rm -rf dist
	rm -rf msgpact_cli/msgpact
	rm -rf tmp
	rm msgpact_cli/LICENSE msgpact_cli/NOTICE
	poetry env remove --all

test:
	poetry run msgpact codegen --schema-dir tests/data --lang java --out tests/output/java --package output
	poetry run msgpact codegen --schema-dir tests/data --lang py --out tests/output/py
	poetry run msgpact codegen --schema-dir tests/data --lang ts --out tests/output/ts