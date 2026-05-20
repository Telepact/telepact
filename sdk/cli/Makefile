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

.PHONY: all dep clean docker

VERSION := $(shell cat ../../VERSION.txt)

SRC_FILES := $(shell find telepact_cli \
	-type d \( -name __pycache__ -o -path 'telepact_cli/telepact' \) -prune -o \
	-type f -print)
TAR_GZ := dist/*.tar.gz
DEP_TAR_GZ := ../../lib/py/dist/*.tar.gz
DOCKER_DIST := dist-docker/docker-image-telepact-cli-$(VERSION).tar.gz

$(TAR_GZ): $(DEP_TAR_GZ) $(SRC_FILES)
	cp ../../LICENSE ../../NOTICE ./
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf $(DEP_TAR_GZ) -C tmp
	rm -rf telepact_cli/telepact
	mv tmp/*/telepact telepact_cli/telepact
	rm -rf tmp

	rm -rf dist
	uv sync --all-groups
	uv build

$(DEP_TAR_GZ):
	$(MAKE) -C ../../lib/py

$(DOCKER_DIST): $(TAR_GZ)
	mkdir tmp
	cp dist/telepact_cli-*.tar.gz tmp/telepact_cli.tar.gz

	docker build --progress=plain --no-cache -f Dockerfile -t telepact-cli:${VERSION} .

	rm -rf tmp

	mkdir -p dist-docker
	docker save telepact-cli:${VERSION} | gzip > dist-docker/docker-image-telepact-cli-${VERSION}.tar.gz

docker: $(DOCKER_DIST)

clean:
	rm -rf dist
	rm -rf dist-docker
	rm -rf telepact_cli/telepact
	rm -rf tmp
	rm -f LICENSE NOTICE
	rm -rf .venv
	rm -f uv.lock
	rm -rf build

test:
	uv run python -m pytest -s -vv

old-test:
	uv run telepact codegen --schema-dir tests/data --lang java --out tests/output/java --package output
	uv run telepact codegen --schema-dir tests/data --lang py --out tests/output/py
	uv run telepact codegen --schema-dir tests/data --lang ts --out tests/output/ts

deploy: $(TAR_GZ)
	uv publish
