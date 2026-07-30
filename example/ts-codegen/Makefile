#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash

.PHONY: run dep codegen clean

run: codegen
	@set -euo pipefail; \
	$(MAKE) -C ../../lib/ts; \
	rm -rf node_modules dist telepact.tgz; \
	cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz; \
	npm install --ignore-scripts --no-package-lock; \
	npm run build; \
	npm test

dep:
	@$(MAKE) -C ../../lib/ts

codegen: dep
	@set -euo pipefail; \
	rm -rf ../../sdk/cli/telepact_cli/telepact; \
	cp -r ../../lib/py/telepact ../../sdk/cli/telepact_cli/telepact; \
	rm -rf gen; \
	mkdir -p gen; \
	uv run --project ../../sdk/cli telepact codegen --schema-dir api --lang ts --out gen; \
	: > gen/.license-header-ignore

clean:
	@rm -rf dist node_modules telepact.tgz gen
