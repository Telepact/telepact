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

LIB_TAR_GZ := ../../lib/ts/dist-tgz/*.tgz
TAR_GZ := telepact.tgz
NPM_STAMP := node_modules/.package-lock.stamp

.PHONY: run clean

run: $(NPM_STAMP)
	npm test

$(TAR_GZ):
	$(MAKE) -C ../../lib/ts
	cp $(LIB_TAR_GZ) $(TAR_GZ)

$(NPM_STAMP): package.json package-lock.json $(TAR_GZ)
	$(MAKE) -C ../../sdk/cli
	$(MAKE) -C ../.. install-cli
	npm install --ignore-scripts
	npm install --ignore-scripts --no-save ./$(TAR_GZ)
	mkdir -p node_modules
	touch $(NPM_STAMP)

clean:
	rm -rf node_modules
	rm -rf playwright-report
	rm -rf test-results
	rm -f $(TAR_GZ)
