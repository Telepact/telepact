# Runner Tests

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

## Required Style

- Define new cases in a `*_cases.py` module inside `parameters/`.
- Express each case as request/expected-response data, matching the existing
  `cases = { "name": [[request, response], ...] }` pattern.
- Keep the executable test modules thin. They should mostly:
  - start the right server fixture
  - hand each request to `verify_*_case(...)`
  - rely on `conftest.py` for parametrization

## Avoid

- Writing one-off assertion-heavy tests that inspect responses imperatively in
  the test body.
- Embedding large custom verification logic directly in `test_*.py` files when
  the same behavior can be captured as request/expected-response data.

## When Adding A New Test Family

1. Add a new `parameters/<name>_cases.py` module.
2. Register it in [`conftest.py`](./conftest.py).
3. Keep the matching `test_<name>.py` file as a small transport fixture plus a
   simple `verify_*_case(...)` loop.
