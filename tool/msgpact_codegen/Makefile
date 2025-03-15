.PHONY: all dep clean

all: dep
	cp ../../LICENSE ../../NOTICE msgpact_codegen
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf ../../lib/py/dist/*.tar.gz -C tmp
	rm -rf msgpact_codegen/msgpact
	mv tmp/*/msgpact msgpact_codegen/msgpact
	rm -rf tmp

	rm -rf dist
	poetry install
	poetry build

dep:
	cd ../../lib/py && make

clean:
	rm -rf dist
	rm -rf msgpact_codegen/msgpact
	rm -rf tmp
	rm msgpact_codegen/LICENSE msgpact_codegen/NOTICE
	poetry env remove --all