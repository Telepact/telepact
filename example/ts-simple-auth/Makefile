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

SHELL := /bin/bash

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf .venv node_modules dist telepact.tgz; \
	uv venv --python python3.11 .venv; \
	uv pip install --python .venv/bin/python ../../lib/py/dist/*.tar.gz; \
	cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz; \
	npm install --ignore-scripts --no-package-lock; \
	npm run build; \
	npm test

clean:
	@rm -rf .venv dist node_modules telepact.tgz
