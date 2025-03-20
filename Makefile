java:
	cd lib/java && make

clean-java:
	cd lib/java && make clean

test-java:
	cd qa/test && make test-java

test-trace-java:
	cd qa/test && make test-trace-java

py:
	cd lib/py && make

clean-py:
	cd lib/py && make clean

test-py:
	cd qa/test && make test-py

test-trace-py:
	cd qa/test && make test-trace-py

ts:
	cd lib/ts && make

clean-ts:
	cd lib/ts && make clean

test-ts:
	cd qa/test && make test-ts

test-trace-ts:
	cd qa/test && make test-trace-ts

test:
	cd qa/test && make test

dart:
	cd bind/dart && make

clean-dart:
	cd bind/dart && make clean

test-dart:
	cd bind/dart && make test

cli:
	cd tool/cli && make

clean-cli:
	cd tool/cli && make clean

install-cli:
	pipx install $(wildcard tool/cli/dist/msgpact_cli-*.tar.gz)

uninstall-cli:
	pipx uninstall msgpact-cli

prettier:
	cd tool/prettier-plugin-msgpact && make

clean-prettier:
	cd tool/prettier-plugin-msgpact && make clean

console:
	cd tool/console && make

dev-console:
	cd tool/console && make dev

clean-console:
	cd tool/console && make clean

test-console:
	cd tool/console && make test

docker:
	cd tool/docker && make

dev-docker:
	cd tool/docker && make dev

test-docker:
	cd tool/docker && make test

clean-docker:
	cd tool/docker && make clean