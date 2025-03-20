VERSION := $(shell cat VERSION.txt)

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
	pipx install $(wildcard sdk/cli/dist/msgpact_cli-*.tar.gz)

uninstall-cli:
	pipx uninstall msgpact-cli

prettier:
	cd sdk/prettier-plugin-msgpact && make

clean-prettier:
	cd sdk/prettier-plugin-msgpact && make clean

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
	cd tool/msgpact_project_cli && make

clean-project-cli:
	cd tool/msgpact_project_cli && make clean

install-project-cli:
	pipx install $(wildcard tool/msgpact_project_cli/dist/msgpact_project_cli-*.tar.gz)

uninstall-project-cli:
	pipx uninstall msgpact-project

version:
	cd lib/java && msgpact-project set-version ${VERSION}
	cd lib/py && msgpact-project set-version ${VERSION}
	cd lib/ts && msgpact-project set-version ${VERSION}
	cd bind/dart && msgpact-project set-version ${VERSION}
	cd sdk/cli && msgpact-project set-version ${VERSION}
	cd sdk/prettier-plugin-msgpact && msgpact-project set-version ${VERSION}
	cd sdk/console && msgpact-project set-version ${VERSION}

