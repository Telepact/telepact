.PHONY: all clean

all:
	mkdir -p telepact/json
	cp ../../common/*.json telepact/json
	cp ../../LICENSE ../../NOTICE telepact/
	
	rm -rf dist
	poetry install
	poetry build

clean:
	rm -rf dist
	rm -rf telepact/json
	rm -f telepact/LICENSE telepact/NOTICE
	poetry env remove --all