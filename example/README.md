# Telepact examples

These examples are one-shot demonstration tests. Each one starts the minimal transport wiring it needs, sends an example request/response exchange, then tears down and exits.

| Directory | Pattern | Test command |
| --- | --- | --- |
| `java-http-basic` | Basic HTTP transport | `make -C ../../lib/java && mvn -q -s settings.xml -Dtelepact.version=$(cat ../../VERSION.txt) test` |
| `ts-http-cookie-auth` | Cookie-backed auth | `make -C ../../lib/ts && cp ../../lib/ts/dist-tgz/*.tgz telepact.tgz && npm install && npm test` |
| `go-websocket` | WebSocket transport | `go test ./...` |
| `py-select` | `@select_` response shaping | `make -C ../../lib/py && rm -rf .venv && uv venv --python python3.11 .venv && uv pip install --python .venv/bin/python pytest ../../lib/py/dist/*.tar.gz && .venv/bin/python -m pytest -q` |
| `java-binary` | Binary negotiation | `make -C ../../lib/java && mvn -q -s settings.xml -Dtelepact.version=$(cat ../../VERSION.txt) test` |
| `py-headers` | Request ids and warning headers | `make -C ../../lib/py && rm -rf .venv && uv venv --python python3.11 .venv && uv pip install --python .venv/bin/python pytest ../../lib/py/dist/*.tar.gz && .venv/bin/python -m pytest -q` |
| `go-api-introspection` | `fn.api_` schema introspection | `go test ./...` |
| `py-errors` | `errors.*` result unions | `make -C ../../lib/py && rm -rf .venv && uv venv --python python3.11 .venv && uv pip install --python .venv/bin/python pytest ../../lib/py/dist/*.tar.gz && .venv/bin/python -m pytest -q` |
| `py-links` | Function-type links | `make -C ../../lib/py && rm -rf .venv && uv venv --python python3.11 .venv && uv pip install --python .venv/bin/python pytest ../../lib/py/dist/*.tar.gz && .venv/bin/python -m pytest -q` |
