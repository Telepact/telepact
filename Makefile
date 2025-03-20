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

msgpact-version:
	cd tool/msgpact_version && make

clean-msgpact-version:
	cd tool/msgpact_version && make clean

install-msgpact-version:
	pipx install $(wildcard tool/msgpact_version/dist/msgpact_version-*.tar.gz)

uninstall-msgpact-version:
	pipx uninstall msgpact-version

version:
	cd lib/java && msgpact-version apply ${VERSION}
	cd lib/py && msgpact-version apply ${VERSION}
	cd lib/ts && msgpact-version apply ${VERSION}
	cd sdk/cli && msgpact-version apply ${VERSION}
	cd sdk/prettier-plugin-msgpact && msgpact-version apply ${VERSION}
	cd sdk/console && msgpact-version apply ${VERSION}
