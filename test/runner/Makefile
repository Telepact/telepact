test: setup
	poetry run python -m pytest

test-java: setup
	poetry run python -m pytest -k [java

test-trace-java: setup
	poetry run python -m pytest -k test_client_server_case[java-0] -s -vv

test-py: setup
	poetry run python -m pytest -k [py

test-trace-py: setup
	poetry run python -m pytest -k test_client_server_case[py-0] -s -vv

test-ts: setup
	poetry run python -m pytest -k [ts

test-trace-ts: setup
	poetry run python -m pytest -k test_client_server_case[ts-0] -s -vv

setup:
	poetry install