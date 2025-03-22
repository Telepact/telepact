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

test: setup java py ts
	poetry run python -m pytest

test-java: setup java
	poetry run python -m pytest -k [java

test-trace-java: setup java
	poetry run python -m pytest -k test_client_server_case[java-0] -s -vv

test-py: setup py
	poetry run python -m pytest -k [py

test-trace-py: setup py
	poetry run python -m pytest -k test_client_server_case[py-0] -s -vv

test-ts: setup ts
	poetry run python -m pytest -k [ts

test-trace-ts: setup ts
	poetry run python -m pytest -k test_client_server_case[ts-0] -s -vv

setup:
	poetry install

java:
	cd ../lib/java && make

py:
	cd ../lib/py && make

ts:
	cd ../lib/ts && make

clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	poetry env remove --all