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

NPM_INSTALL ?= install --ignore-scripts
TAR_GZ := dist-tgz/*.tgz
DEP_LIB_FILE := ../../lib/ts/dist/index.esm.js
DEP_PRETTIER_FILE := ../../sdk/prettier/dist/index.esm.js
NPM_STAMP := node_modules/.package-lock.stamp

.PHONY: all prepare-local-deps dev playwright clean test dev-proxy deploy

all: $(TAR_GZ)

prepare-local-deps: $(DEP_LIB_FILE) $(DEP_PRETTIER_FILE)
	cp ../../LICENSE ../../NOTICE ./
	
	rm -rf src/lib/telepact
	mkdir -p src/lib/telepact
	cp -r ../../lib/ts/dist/* src/lib/telepact

	rm -rf src/lib/prettier-plugin-telepact
	mkdir -p src/lib/prettier-plugin-telepact
	cp -r ../../sdk/prettier/dist/* src/lib/prettier-plugin-telepact

$(NPM_STAMP): package.json package-lock.json
	npm $(NPM_INSTALL)
	mkdir -p node_modules
	touch $(NPM_STAMP)

$(TAR_GZ): prepare-local-deps $(NPM_STAMP)
	rm -rf dist-tgz
	mkdir -p dist-tgz	

	npm run build
	node clean-index.js
	npm pack --pack-destination ./dist-tgz

$(DEP_LIB_FILE):
	$(MAKE) -C ../../lib/ts

$(DEP_PRETTIER_FILE):
	$(MAKE) -C ../../sdk/prettier

dev:
	npm run dev

playwright: $(NPM_STAMP)
	npx playwright install --with-deps --force

clean:
	rm -rf build
	rm -rf src/lib/telepact
	rm -rf src/lib/prettier-plugin-telepact
	rm -rf node_modules
	rm -rf dist-tgz
	rm -rf LICENSE
	rm -rf NOTICE

test: prepare-local-deps $(NPM_STAMP)
	npm run test

dev-proxy:
	node proxy-server.cjs

deploy: $(TAR_GZ)
	npm publish
