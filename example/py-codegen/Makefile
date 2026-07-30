#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

SHELL := /bin/bash
PYTHON := .venv/bin/python

.PHONY: run dep codegen clean

run: codegen
	@set -euo pipefail; rm -rf .venv; uv venv --python python3.11 .venv; uv pip install --python $(PYTHON) pytest ../../lib/py/dist/*.tar.gz; $(PYTHON) -m pytest -q

dep:
	@$(MAKE) -C ../../lib/py

codegen: dep
	@set -euo pipefail; rm -rf ../../sdk/cli/telepact_cli/telepact; cp -r ../../lib/py/telepact ../../sdk/cli/telepact_cli/telepact; rm -rf gen; uv run --project ../../sdk/cli telepact codegen --schema-dir api --lang py --out gen; printf '\n' > gen/.license-header-ignore

clean:
	@rm -rf .venv
