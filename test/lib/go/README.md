## Go test harness

This harness provides the Go runtime for the shared integration tests that live under `test/runner`.

### Build & install dependencies

```sh
make
```

### Run the dispatcher locally

```sh
NATS_URL=nats://127.0.0.1:4222 make test-server
```

The harness writes Prometheus metrics to `metrics.txt` when it shuts down.
