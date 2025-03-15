.PHONY: all clean

all:
	mkdir -p msgpact/json
	cp ../../common/*.json msgpact/json
	cp ../../LICENSE ../../NOTICE msgpact/
	
	rm -rf dist
	poetry install
	poetry build

clean:
	rm -rf dist
	rm -rf msgpact/json
	rm -f msgpact/LICENSE msgpact/NOTICE
	poetry env remove --all