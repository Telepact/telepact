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

NPM_INSTALL ?= install
VERSION := $(shell cat ../../VERSION.txt)
DEP_LIB_DIST := ../../lib/ts/dist
DEP_PRETTIER_DIST := ../../sdk/prettier/dist

.PHONY: all

all: $(DEP_LIB_DIST) $(DEP_PRETTIER_DIST)
	cp ../../LICENSE ../../NOTICE ./
	
	rm -rf src/lib/telepact
	mkdir -p src/lib/telepact
	cp -r ../../lib/ts/dist/* src/lib/telepact

	rm -rf src/lib/prettier-plugin-telepact
	mkdir -p src/lib/prettier-plugin-telepact
	cp -r ../../sdk/prettier/dist/* src/lib/prettier-plugin-telepact

	rm -rf dist-tgz
	mkdir -p dist-tgz	

	npm $(NPM_INSTALL)
	npm run build
	node clean-index.js
	npm pack --pack-destination ./dist-tgz

	mkdir -p dist

	docker build --progress=plain --no-cache -f Dockerfile -t telepact-console:${VERSION} .
	docker save telepact-console:${VERSION} | gzip > dist/docker-image-telepact-console-${VERSION}.tar.gz

$(DEP_LIB_DIST):
	$(MAKE) -C ../../lib/ts

$(DEP_PRETTIER_DIST):
	$(MAKE) -C ../../sdk/prettier

dev:
	npm run dev

playwright:
	npx playwright install --with-deps --force

clean:
	rm -rf build
	rm -rf src/lib/telepact
	rm -rf src/lib/prettier-plugin-telepact
	rm -rf node_modules
	rm -rf dist
	rm -rf dist-tgz
	rm -rf LICENSE
	rm -rf NOTICE

test:
	npm run test

dev-proxy:
	node proxy-server.cjs