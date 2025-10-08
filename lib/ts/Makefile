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
SRC_FILES := $(shell find src -type f)
TAR_GZ := dist-tgz/*.tgz

.PHONY: clean

$(TAR_GZ): $(SRC_FILES)
	rm -rf inc
	mkdir -p inc
	cp ../../common/*.json inc

	rm -rf dist
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist

	rm -rf dist-tgz
	mkdir -p dist-tgz

	npm $(NPM_INSTALL)
	npm run build
	npm pack --pack-destination ./dist-tgz

clean:
	rm -rf inc
	rm -rf dist
	rm -rf dist-tgz
	rm -rf node_modules
	rm -f dist/LICENSE dist/NOTICE

deploy: $(TAR_GZ)
	npm publish
