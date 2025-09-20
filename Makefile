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
	$(MAKE) -C lib/java

clean-java:
	$(MAKE) -C lib/java clean

test-java:
	$(MAKE) -C test/runner test-java

test-trace-java:
	$(MAKE) -C test/runner test-trace-java

deploy-java:
	$(MAKE) -C lib/java deploy

py:
	$(MAKE) -C lib/py

clean-py:
	$(MAKE) -C lib/py clean

test-py:
	$(MAKE) -C test/runner test-py

test-trace-py:
	$(MAKE) -C test/runner test-trace-py

ts:
	$(MAKE) -C lib/ts

clean-ts:
	$(MAKE) -C lib/ts clean

test-ts:
	$(MAKE) -C test/runner test-ts

test-trace-ts:
	$(MAKE) -C test/runner test-trace-ts

deploy-ts:
	$(MAKE) -C lib/ts deploy

.PHONY: test
test:
	$(MAKE) -C test/runner test

clean-test:
	$(MAKE) -C test/runner clean
	$(MAKE) -C test/lib/java clean
	$(MAKE) -C test/lib/py clean
	$(MAKE) -C test/lib/ts clean

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

install-cli:
	pipx install $(wildcard sdk/cli/dist/telepact_cli-*.tar.gz)

uninstall-cli:
	pipx uninstall telepact-cli

prettier:
	$(MAKE) -C sdk/prettier

clean-prettier:
	$(MAKE) -C sdk/prettier clean

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
	pipx install tool/telepact_project_cli

uninstall-project-cli:
	pipx uninstall telepact-project-cli

version:
	cd lib/java && telepact-project set-version ${VERSION}
	cd lib/py && telepact-project set-version ${VERSION}
	cd lib/ts && telepact-project set-version ${VERSION}
	cd bind/dart && telepact-project set-version ${VERSION}
	cd sdk/cli && telepact-project set-version ${VERSION}
	cd sdk/prettier && telepact-project set-version ${VERSION}
	cd sdk/console && telepact-project set-version ${VERSION}

license-header:
	telepact-project license-header NOTICE
