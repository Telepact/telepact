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

LIB_TAR_GZ := ../../../lib/ts/dist-tgz/*.tgz
TAR_GZ := telepact.tgz
NPM_ENV := NPM_CONFIG_CACHE=/tmp/telepact-npm-cache

all: codegen $(TAR_GZ) link-telepact
	@if [ ! -d node_modules ]; then $(NPM_ENV) npm install --ignore-scripts; fi
	$(NPM_ENV) npm run build

$(TAR_GZ): dep
	cp $(LIB_TAR_GZ) telepact.tgz

dep:
	$(MAKE) -C ../../../lib/ts

link-telepact:
	mkdir -p node_modules
	rm -rf node_modules/telepact
	ln -s ../../../../lib/ts node_modules/telepact
	rm -rf node_modules/crc-32
	ln -s ../../../../lib/ts/node_modules/crc-32 node_modules/crc-32
	rm -rf node_modules/msgpackr
	ln -s ../../../../lib/ts/node_modules/msgpackr node_modules/msgpackr
	rm -rf node_modules/@msgpackr-extract
	ln -s ../../../../lib/ts/node_modules/@msgpackr-extract node_modules/@msgpackr-extract

codegen:
	telepact codegen --schema-dir ../../runner/schema/example --lang ts --out src/gen

test-server: codegen link-telepact
	$(NPM_ENV) npm run build
	$(NPM_ENV) npm start

clean:
	rm -f telepact.tgz
	rm -rf src/gen
	rm -rf dist
	rm -rf node_modules
	rm -f package-lock.json
	$(MAKE) -C ../../../lib/ts clean
