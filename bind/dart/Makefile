#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

VERSION := $(shell cat ../../VERSION.txt)
JS_ASSETS := lib/js/telepact.js lib/js/crc32.js lib/js/msgpackr.js

.PHONY: all prepare-js-assets test

all: prepare-js-assets
	cp ../../LICENSE ../../NOTICE ./
	cat LICENSE_SUB_PROJECT >> LICENSE

	dart pub get

	dart analyze

	mkdir -p dist
	tar -czvf dist/telepact-${VERSION}.tar.gz lib test pubspec.yaml README.md LICENSE NOTICE

prepare-js-assets: $(JS_ASSETS)

lib/js/telepact.js: ../../lib/ts/dist/index.iife.js
	mkdir -p lib/js
	cp ../../lib/ts/dist/index.iife.js lib/js/telepact.js

lib/js/crc32.js lib/js/msgpackr.js &: package-lock.json package.json rollup.crc32.config.js rollup.msgpackr.config.js
	npm install --ignore-scripts
	npx rollup -c rollup.crc32.config.js
	npx rollup -c rollup.msgpackr.config.js
	mkdir -p lib/js
	cp rollup/crc32.iife.js lib/js/crc32.js
	cp rollup/msgpackr.iife.js lib/js/msgpackr.js

../../lib/ts/dist/index.iife.js:
	$(MAKE) -C ../../lib/ts

dep:
	$(MAKE) -C ../../lib/ts

clean:
	rm -rf lib/js
	rm -rf dist
	rm -rf rollup
	rm -rf node_modules
	rm -f LICENSE NOTICE
	rm -rf .dart_tool

.PHONY: test
test:
	$(MAKE) prepare-js-assets
	dart pub get
	dart test -p chrome --chain-stack-traces
