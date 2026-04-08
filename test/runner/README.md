To run the cross-language runner reliably, prefer the repo-root targets that
refresh the per-language test consumers first:

```sh
make test-java
make test-py
make test-ts
make test-go
```

If you are already in `test/runner`, use the matching local targets:

```sh
make test-java
make test-py
make test-ts
make test-go
```

For focused debugging, run pytest directly only after the matching consumer has
already been prepared:

```sh
uv run python -m pytest -k test_client_server_case[py-0] -s -vv
```
