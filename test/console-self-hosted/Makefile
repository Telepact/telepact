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
NPM_INSTALL_STAMP := node_modules/.package-lock.stamp
CONSOLE_BUILD_STAMP := ../../sdk/console/build/index.html
CONSOLE_PACKAGE_FILES := ../../sdk/console/package.json ../../sdk/console/cli.js ../../sdk/console/self-hosted.js ../../sdk/console/LICENSE ../../sdk/console/NOTICE $(CONSOLE_BUILD_STAMP)

all: telepact-console-self-host.image

$(NPM_INSTALL_STAMP): package.json package-lock.json
	npm install --ignore-scripts
	mkdir -p node_modules
	touch $(NPM_INSTALL_STAMP)

$(CONSOLE_BUILD_STAMP):
	$(MAKE) -C ../../sdk/console

telepact-console-self-host.image: $(CONSOLE_PACKAGE_FILES) Dockerfile $(NPM_INSTALL_STAMP)
	docker build --progress=plain --no-cache -f Dockerfile -t telepact-console-self-host:${VERSION} ../..
	touch telepact-console-self-host.image

clean:
	rm -rf node_modules
	rm -f package-lock.json
	rm -f telepact-console-self-host.image

test: telepact-console-self-host.image
	npm run test
