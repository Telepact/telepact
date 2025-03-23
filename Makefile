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

VERSION := $(shell cat VERSION.txt)

noop:
	@echo "No-op. Specify a target."

java:
	cd lib/java && make

clean-java:
	cd lib/java && make clean

test-java:
	cd test/runner && make test-java

test-trace-java:
	cd test/runner && make test-trace-java

py:
	cd lib/py && make

clean-py:
	cd lib/py && make clean

test-py:
	cd test/runner && make test-py

test-trace-py:
	cd test/runner && make test-trace-py

ts:
	cd lib/ts && make

clean-ts:
	cd lib/ts && make clean

test-ts:
	cd test/runner && make test-ts

test-trace-ts:
	cd test/runner && make test-trace-ts

.PHONY: test
test:
	cd test/runner && make test

clean-test:
	cd test/runner && make clean
	cd test/lib/java && make clean
	cd test/lib/py && make clean
	cd test/lib/ts && make clean

dart:
	cd bind/dart && make

clean-dart:
	cd bind/dart && make clean

test-dart:
	cd bind/dart && make test

cli:
	cd sdk/cli && make

clean-cli:
	cd sdk/cli && make clean

install-cli:
	pipx install $(wildcard sdk/cli/dist/telepact_cli-*.tar.gz)

uninstall-cli:
	pipx uninstall telepact-cli

prettier:
	cd sdk/prettier-plugin-telepact && make

clean-prettier:
	cd sdk/prettier-plugin-telepact && make clean

console:
	cd sdk/console && make

dev-console:
	cd sdk/console && make dev

clean-console:
	cd sdk/console && make clean

test-console:
	cd sdk/console && make test

docker:
	cd sdk/docker && make

dev-docker:
	cd sdk/docker && make dev

test-docker:
	cd sdk/docker && make test

clean-docker:
	cd sdk/docker && make clean

project-cli:
	cd tool/telepact_project_cli && make

clean-project-cli:
	cd tool/telepact_project_cli && make clean

install-project-cli:
	pipx install $(wildcard tool/telepact_project_cli/dist/telepact_project_cli-*.tar.gz)

uninstall-project-cli:
	pipx uninstall telepact-project-cli

version:
	cd lib/java && telepact-project set-version ${VERSION}
	cd lib/py && telepact-project set-version ${VERSION}
	cd lib/ts && telepact-project set-version ${VERSION}
	cd bind/dart && telepact-project set-version ${VERSION}
	cd sdk/cli && telepact-project set-version ${VERSION}
	cd sdk/prettier-plugin-telepact && telepact-project set-version ${VERSION}
	cd sdk/console && telepact-project set-version ${VERSION}

bump-version:
	telepact-project bump VERSION.txt \
		lib/java/pom.xml  
		lib/py/setup.py \
		lib/ts/package.json \
		bind/dart/pubspec.yaml \
		sdk/cli/setup.py \
		sdk/prettier-plugin-telepact/package.json \
		sdk/console/setup.py

license-header:
	telepact-project license-header NOTICE
