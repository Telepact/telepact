#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash
PYTHON := .venv/bin/python

.PHONY: run clean

run:
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/py; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf .venv node_modules dist telepact.tgz; \
	uv venv --python python3.11 .venv; \
	uv pip install --python $(PYTHON) ../../lib/py/dist/*.tar.gz; \
	cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz; \
	npm install --ignore-scripts --no-package-lock; \
	npm run build; \
	npm test

clean:
	@rm -rf .venv dist node_modules telepact.tgz
