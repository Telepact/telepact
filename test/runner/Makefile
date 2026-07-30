#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

test: setup java py ts go
	uv run python -m pytest

test-java:
	$(MAKE) prepare-java
	$(MAKE) test-java-run

prepare-java: setup java

test-java-run: setup
	uv run python -m pytest -k [java

test-trace-java: prepare-java
	uv run python -m pytest -k test_client_server_case[java-0] -s -vv

test-py:
	$(MAKE) prepare-py
	$(MAKE) test-py-run

prepare-py: setup py

test-py-run: setup
	uv run python -m pytest -k [py

test-trace-py: prepare-py
	uv run python -m pytest -k test_client_server_case[py-0] -s -vv

test-ts:
	$(MAKE) prepare-ts
	$(MAKE) test-ts-run

prepare-ts: setup ts

test-ts-run: setup
	uv run python -m pytest -k [ts

test-trace-ts: prepare-ts
	uv run python -m pytest -k test_client_server_case[ts-0] -s -vv

test-go:
	$(MAKE) prepare-go
	$(MAKE) test-go-run

prepare-go: setup go

test-go-run: setup
	uv run python -m pytest -k [go

test-trace-go: prepare-go
	uv run python -m pytest -k test_client_server_case[go-0] -s -vv

setup:
	uv sync --all-groups

java:
	$(MAKE) -C ../lib/java

py:
	$(MAKE) -C ../lib/py

ts:
	$(MAKE) -C ../lib/ts

go:
	$(MAKE) -C ../lib/go

clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf .venv
	rm -f uv.lock

.PHONY: test test-java prepare-java test-java-run test-trace-java test-py prepare-py test-py-run test-trace-py test-ts prepare-ts test-ts-run test-trace-ts test-go prepare-go test-go-run test-trace-go setup java py ts go clean
