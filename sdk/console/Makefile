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

.PHONY: all

all: dep
	cp ../../LICENSE ../../NOTICE ./
	
	rm -rf src/lib/telepact
	mkdir -p src/lib/telepact
	cp -r ../../lib/ts/dist/* src/lib/telepact

	rm -rf src/lib/prettier-plugin-telepact
	mkdir -p src/lib/prettier-plugin-telepact
	cp -r ../../sdk/prettier/dist/* src/lib/prettier-plugin-telepact

	npm install
	npm run build
	node clean-index.js

	mkdir -p dist

	docker build --progress=plain --no-cache -f Dockerfile -t telepact-console:${VERSION} .
	docker save telepact-console:${VERSION} | gzip > dist/docker-image-telepact-console-${VERSION}.tar.gz


dep:
	$(MAKE) -C ../../lib/ts
	$(MAKE) -C ../../sdk/prettier

dev:
	npm run dev

clean:
	rm -rf build
	rm -rf src/lib/telepact
	rm -rf src/lib/prettier-plugin-telepact
	rm -rf node_modules
	rm -rf dist
	rm -rf LICENSE
	rm -rf NOTICE

test:
	npm run test