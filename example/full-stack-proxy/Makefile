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
PYTHON := proxy/.venv/bin/python

.PHONY: run clean

run:
@set -euo pipefail; \
$(MAKE) -C ../../lib/go; \
$(MAKE) -C ../../lib/ts; \
rm -rf proxy/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz server/bin; \
uv venv --python python3.11 proxy/.venv; \
uv pip install --python $(PYTHON) -r proxy/requirements.txt; \
cp ../../lib/ts/dist-tgz/*.tgz client/telepact.tgz; \
(cd client && npm install --ignore-scripts --no-package-lock); \
(cd client && npm run build); \
mkdir -p server/bin; \
(cd server && GOTOOLCHAIN=local go build -o ./bin/full-stack-proxy-server .); \
(cd client && npx playwright install chromium); \
(cd client && npm test)

clean:
@rm -rf proxy/.venv client/node_modules client/dist client/playwright-report client/test-results client/telepact.tgz server/bin
