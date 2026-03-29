# Telepact examples

Each example is intentionally minimal and focuses on one Telepact pattern.

Common commands:

- In any example directory, run `make run` to start the example.
- In any example directory, run `make check` to verify the example end to end.
- From this directory, run `make check` to verify every example in CI.

| Directory | Pattern | What it shows |
| --- | --- | --- |
| `java-http-basic` | Basic HTTP transport | A minimal Java Telepact server wired to one HTTP POST endpoint. |
| `ts-http-cookie-auth` | Cookie-backed auth | A TypeScript transport adapter that reads a session cookie and maps it to `@auth_`. |
| `go-websocket` | WebSocket transport | One Telepact request per WebSocket message using a Go server. |
| `py-select` | `@select_` response shaping | A Python server that returns full data while Telepact trims the response graph. |
| `java-binary` | Binary negotiation | A Java client/server pair that upgrades from JSON to Telepact binary payloads. |
