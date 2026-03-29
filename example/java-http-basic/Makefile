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

SHELL := /bin/bash
PORT ?= 8091
VERSION := $(shell cat ../../VERSION.txt)
MAVEN := mvn -q -s settings.xml -Dtelepact.version=$(VERSION)

.PHONY: prepare run run-server check check-client clean

prepare:
	$(MAKE) -C ../../lib/java
	$(MAVEN) compile

run: prepare
	$(MAKE) run-server

run-server:
	$(MAVEN) exec:java -Dexec.args="server $(PORT)"

check-client: prepare
	$(MAVEN) exec:java -Dexec.args="check http://127.0.0.1:$(PORT)/api/telepact"

check: prepare
	@set -euo pipefail; \
	log_file=$$(mktemp); \
	cleanup() { if [ -n "$${server_pid:-}" ] && kill -0 $$server_pid 2>/dev/null; then kill $$server_pid; wait $$server_pid || true; fi; rm -f $$log_file; }; \
	trap cleanup EXIT; \
	$(MAKE) run-server >$$log_file 2>&1 & server_pid=$$!; \
	for _ in $$(seq 1 30); do \
		if curl -fsS http://127.0.0.1:$(PORT)/healthz >/dev/null 2>&1; then break; fi; \
		sleep 1; \
	done; \
	curl -fsS http://127.0.0.1:$(PORT)/healthz >/dev/null; \
	$(MAKE) check-client

clean:
	rm -rf target .m2
