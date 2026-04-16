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

.PHONY: run dep codegen clean

run: codegen
	@set -euo pipefail; rm -rf .venv; uv venv --python python3.11 .venv; uv pip install --python $(PYTHON) pytest ../../lib/py/dist/*.tar.gz; $(PYTHON) -m pytest -q

dep:
	@$(MAKE) -C ../../lib/py

codegen: dep
	@set -euo pipefail; rm -rf ../../sdk/cli/telepact_cli/telepact; cp -r ../../lib/py/telepact ../../sdk/cli/telepact_cli/telepact; rm -rf gen; uv run --project ../../sdk/cli telepact codegen --schema-dir api --lang py --out gen

clean:
	@rm -rf .venv gen
