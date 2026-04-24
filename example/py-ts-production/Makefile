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
PYTHON := .venv/bin/python

.PHONY: run build-frontend setup-backend compare playwright serve clean

run: compare build-frontend
	@set -euo pipefail; \
	rm -rf .venv; \
	uv venv --python python3.11 .venv; \
	uv pip install --python $(PYTHON) ../../lib/py/dist/*.tar.gz; \
	npx playwright install --with-deps chromium; \
	npm test

build-frontend:
	@set -euo pipefail; \
	rm -rf node_modules dist-web; \
	npm install --ignore-scripts --no-package-lock; \
	npm run build

setup-backend:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	rm -rf .venv; \
	uv venv --python python3.11 .venv; \
	uv pip install --python $(PYTHON) ../../lib/py/dist/*.tar.gz

compare:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	rm -rf ../../sdk/cli/telepact_cli/telepact; \
	cp -r ../../lib/py/telepact ../../sdk/cli/telepact_cli/telepact; \
	trap 'rm -rf ../../sdk/cli/telepact_cli/telepact' EXIT; \
	uv run --project ../../sdk/cli telepact compare --old-schema-dir schema-baseline --new-schema-dir api

playwright: build-frontend setup-backend
	@set -euo pipefail; \
	npx playwright install --with-deps chromium; \
	npm test

serve: build-frontend setup-backend
	@set -euo pipefail; $(PYTHON) server.py

clean:
	@rm -rf .venv dist-web node_modules playwright-report test-results
