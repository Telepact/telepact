# Introduction

Telepact is what happens when JSON, GraphQL, gRPC, and hypermedia keep their
best ideas and drop the baggage. 🚀

Build an API once, serve it over the transport that fits, and let every client
choose its own comfort level: raw JSON when that's enough, schema-backed
libraries when guardrails help, generated code when ergonomics matter, and
binary when performance starts to count. Telepact starts featherweight and
levels up without forcing every consumer into the same toolchain.

Why it lands:

- ✨ **Plain JSON is the default** - clients can integrate with standard JSON
  and networking tools, no mandatory codegen pipeline required
- 🎯 **Response shaping is built in** - clients can ask for less data without
  inventing a second query language
- ⚡ **Binary is optional, not a tax** - efficient serialization is negotiated
  at runtime instead of demanded up front
- 🔗 **Hypermedia-style flows travel anywhere** - APIs can return prefilled
  follow-up calls as data, not just URLs pinned to HTTP
- 🧪 **Schemas pull real weight** - the same definition drives validation,
  docs, mocks, version comparison, and optional code generation

If your team wants APIs that are easy to consume, hard to drift, and ready to
scale from "just send JSON" to "ship the optimized path," Telepact makes a very
convincing case. 🔥

# It's just JSON
No query params. No binary field ids. No required client libraries.

It's just JSON in, and JSON out.

Schema:
```yaml
- fn.helloWorld: {}
  ->:
    - Ok_:
        msg: string
```
Request:
```json
[{}, {"fn.helloWorld": {}}]
```
Response:
```json
[{}, {"Ok_": {"msg": "Hello world!"}}]
```

Check out the [full-stack example](./doc/example.md).

# Explore

Start with the [docs landing page](./doc/index.md) for guides, examples,
library references, SDK tools, version information, and further reading. The
published docs are available at [telepact.github.io/telepact](https://telepact.github.io/telepact).

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](./LICENSE) for the full license text. See [NOTICE](./NOTICE) for
additional information regarding copyright ownership.
