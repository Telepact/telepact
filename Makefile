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

.PHONY: doc-versions
doc-versions:
	telepact-project doc-versions

java:
	$(MAKE) -C lib/java

clean-java:
	$(MAKE) -C lib/java clean

test-java:
	$(MAKE) prepare-test-java
	$(MAKE) test-java-run

prepare-test-java:
	$(MAKE) -C test/lib/java

test-java-run:
	$(MAKE) -C test/runner test-java-run

test-trace-java:
	$(MAKE) -C test/runner test-trace-java

deploy-java:
	$(MAKE) -C lib/java deploy

py:
	$(MAKE) -C lib/py

clean-py:
	$(MAKE) -C lib/py clean

test-py:
	$(MAKE) prepare-test-py
	$(MAKE) test-py-run

prepare-test-py:
	$(MAKE) -C test/lib/py

test-py-run:
	$(MAKE) -C test/runner test-py-run

test-trace-py:
	$(MAKE) -C test/runner test-trace-py

deploy-py:
	$(MAKE) -C lib/py deploy

ts:
	$(MAKE) -C lib/ts

clean-ts:
	$(MAKE) -C lib/ts clean

test-ts:
	$(MAKE) prepare-test-ts
	$(MAKE) test-ts-run

prepare-test-ts:
	$(MAKE) -C test/lib/ts
	$(MAKE) -C test/lib/ts-browser-safe
	$(MAKE) -C test/lib/ts-nodenext

test-ts-run:
	$(MAKE) -C test/runner test-ts-run

test-trace-ts:
	$(MAKE) -C test/runner test-trace-ts

deploy-ts:
	$(MAKE) -C lib/ts deploy

go:
	$(MAKE) -C lib/go

clean-go:
	$(MAKE) -C lib/go clean

test-go:
	$(MAKE) prepare-test-go
	$(MAKE) test-go-run

prepare-test-go:
	$(MAKE) -C test/lib/go

test-go-run:
	$(MAKE) -C test/runner test-go-run

test-trace-go:
	$(MAKE) -C test/runner test-trace-go

deploy-go:
	$(MAKE) -C lib/go deploy

.PHONY: test prepare-test-java test-java-run prepare-test-py test-py-run prepare-test-ts test-ts-run prepare-test-go test-go-run
test:
	$(MAKE) -C test/runner test

clean-test:
	$(MAKE) -C test/runner clean
	$(MAKE) -C test/lib/java clean
	$(MAKE) -C test/lib/py clean
	$(MAKE) -C test/lib/go clean
	$(MAKE) -C test/lib/ts clean
	$(MAKE) -C test/lib/ts-browser-safe clean
	$(MAKE) -C test/lib/ts-nodenext clean

dart:
	$(MAKE) -C bind/dart

clean-dart:
	$(MAKE) -C bind/dart clean

test-dart:
	$(MAKE) -C bind/dart test

cli:
	$(MAKE) -C sdk/cli

clean-cli:
	$(MAKE) -C sdk/cli clean

test-cli:
	$(MAKE) -C sdk/cli test

deploy-cli:
	$(MAKE) -C sdk/cli deploy

install-cli:
	uv tool install --force $(wildcard sdk/cli/dist/telepact_cli-*.whl)

uninstall-cli:
	uv tool uninstall telepact-cli

prettier:
	$(MAKE) -C sdk/prettier

clean-prettier:
	$(MAKE) -C sdk/prettier clean

deploy-prettier:
	$(MAKE) -C sdk/prettier deploy

console:
	$(MAKE) -C sdk/console

console-playwright:
	$(MAKE) -C sdk/console playwright

dev-console:
	$(MAKE) -C sdk/console dev

clean-console:
	$(MAKE) -C sdk/console clean

test-console:
	$(MAKE) -C sdk/console test

deploy-console:
	$(MAKE) -C sdk/console deploy

console-self-hosted:
	$(MAKE) -C test/console-self-hosted

clean-console-self-hosted:
	$(MAKE) -C test/console-self-hosted clean

test-console-self-hosted:
	$(MAKE) -C test/console-self-hosted test

project-cli:
	$(MAKE) -C tool/telepact_project_cli

clean-project-cli:
	$(MAKE) -C tool/telepact_project_cli clean

install-project-cli:
	uv tool install --force tool/telepact_project_cli

uninstall-project-cli:
	uv tool uninstall telepact-project-cli

version:
	cd lib/java && telepact-project set-version ${VERSION}
	cd lib/py && telepact-project set-version ${VERSION}
	cd lib/ts && telepact-project set-version ${VERSION}
	cd bind/dart && telepact-project set-version ${VERSION}
	cd sdk/cli && telepact-project set-version ${VERSION}
	cd sdk/prettier && telepact-project set-version ${VERSION}
	cd sdk/console && telepact-project set-version ${VERSION}
	$(MAKE) doc-versions

license-header:
	telepact-project license-header NOTICE
