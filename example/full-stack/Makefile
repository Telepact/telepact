#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash
PYTHON := server/.venv/bin/python

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf server/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz; \
	uv venv --python python3.11 server/.venv; \
	uv pip install --python $(PYTHON) ../../lib/py/dist/*.tar.gz; \
	cp ../../lib/ts/dist-tgz/*.tgz client/telepact.tgz; \
	(cd client && npm install --ignore-scripts --no-package-lock); \
	(cd client && npm run build); \
	(cd client && npx playwright install chromium); \
	(cd client && npm test)

clean:
	@rm -rf server/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz
