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

LIB_TAR_GZ := ../../lib/py/dist/*.tar.gz
TAR_GZ := telepact.tar.gz

all: prepare

prepare: prepare-py prepare-ts prepare-java

prepare-py: $(TAR_GZ)
	uv sync --all-groups
	uv pip install --python .venv/bin/python ./telepact.tar.gz

$(TAR_GZ): dep-py
	cp $(LIB_TAR_GZ) telepact.tar.gz

dep-py:
	$(MAKE) -C ../../lib/py

prepare-ts:
	$(MAKE) -C ts

prepare-java:
	$(MAKE) -C java

run: prepare
	uv run python -m perf_harness.run

clean:
	rm -f telepact.tar.gz
	rm -rf .venv
	rm -f uv.lock
	rm -rf results
	mkdir -p results
	$(MAKE) -C ts clean
	$(MAKE) -C java clean

.PHONY: all prepare prepare-py dep-py prepare-ts prepare-java run clean
