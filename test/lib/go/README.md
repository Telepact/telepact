## Go test harness

This harness provides the Go runtime for the shared integration tests that live under `test/runner`.

### Build & install dependencies

```sh
make
```

### Run the dispatcher locally

```sh
TP_TRANSPORT_URL=stdio://local make test-server
```

The harness writes Prometheus metrics to `metrics.txt` when it shuts down.
