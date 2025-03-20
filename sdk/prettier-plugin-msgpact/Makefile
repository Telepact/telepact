.PHONY: all

all:
	rm -rf dist
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist
	npm install
	npm run build

clean:
	rm -rf dist
	rm -rf node_modules
