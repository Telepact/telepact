.PHONY: all

all:
	cp ../../LICENSE ../../NOTICE ./
	npm install
	
	npx rollup -c rollup.crc32.config.js
	npx rollup -c rollup.msgpackr.config.js

	mkdir -p lib/js
	cp node_modules/msgpact/dist/index.iife.js lib/js/msgpact.js
	cp dist/crc32.iife.js lib/js/crc32.js
	cp dist/msgpackr.iife.js lib/js/msgpackr.js	

	dart pub get

	dart analyze

clean:
	rm -rf lib/js
	rm -rf dist
	rm -rf node_modules
	rm -f LICENSE NOTICE
	rm -rf .dart_tool

.PHONY: test
test:
	dart test -p chrome