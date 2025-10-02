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

.PHONY: all dep clean

VERSION := $(shell cat ../../VERSION.txt)

SRC_FILES := $(shell find telepact_cli -type f)
TAR_GZ := dist/*.tar.gz
DEP_TAR_GZ := ../../lib/py/dist/*.tar.gz

$(TAR_GZ): $(DEP_TAR_GZ) $(SRC_FILES)
	cp ../../LICENSE ../../NOTICE ./
	rm -rf tmp
	mkdir -p tmp
	tar -xzvf $(DEP_TAR_GZ) -C tmp
	rm -rf telepact_cli/telepact
	mv tmp/*/telepact telepact_cli/telepact
	rm -rf tmp

	rm -rf dist
	poetry lock
	poetry install

	# TODO: Get "include" to work in pyproject.toml
	sed -i '' '/^telepact_cli\/telepact/s/^/#/' .gitignore
	poetry build
	sed -i '' '/^#telepact_cli\/telepact/s/^#//' .gitignore

	mkdir tmp
	cp dist/telepact_cli-*.tar.gz tmp/telepact_cli.tar.gz

	docker build --progress=plain --no-cache -f Dockerfile -t telepact-cli:${VERSION} .

	rm -rf tmp

	mkdir -p docker-dist
	docker save telepact-cli:${VERSION} | gzip > docker-dist/docker-image-telepact-cli-${VERSION}.tar.gz


$(DEP_TAR_GZ):
	$(MAKE) -C ../../lib/py

clean:
	rm -rf dist
	rm -rf docker-dist
	rm -rf telepact_cli/telepact
	rm -rf tmp
	rm -f LICENSE NOTICE
	poetry env remove --all

test:
	poetry run python -m pytest -s -vv

old-test:
	poetry run telepact codegen --schema-dir tests/data --lang java --out tests/output/java --package output
	poetry run telepact codegen --schema-dir tests/data --lang py --out tests/output/py
	poetry run telepact codegen --schema-dir tests/data --lang ts --out tests/output/ts

deploy: $(TAR_GZ)
	# TODO: Get "include" to work in pyproject.toml
	sed -i '' '/^telepact_cli\/telepact/s/^/#/' .gitignore
	poetry publish
	sed -i '' '/^#telepact_cli\/telepact/s/^#//' .gitignore
