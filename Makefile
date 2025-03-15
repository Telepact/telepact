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
	cd port/dart && make

clean-dart:
	cd port/dart && make clean

test-dart:
	cd port/dart && make test

codegen:
	cd tool/msgpact_codegen && make

clean-codegen:
	cd tool/msgpact_codegen && make clean

install-codegen:
	pipx install $(wildcard tool/msgpact_codegen/dist/msgpact_codegen-*.tar.gz)

uninstall-codegen:
	pipx uninstall msgpact-codegen