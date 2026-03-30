# py-headers

Minimal Python Telepact example that runs as a one-shot `pytest` test and verifies `@id_` echoing plus `@warn_` response headers.

Test command:

```bash
make -C ../../lib/py
rm -rf .venv
uv venv --python python3.11 .venv
uv pip install --python .venv/bin/python pytest ../../lib/py/dist/*.tar.gz
.venv/bin/python -m pytest -q
```
