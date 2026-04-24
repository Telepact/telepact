# Introduction

Telepact is a thin but powerful RPC framework built on JSON, enabling accessible
API designs wherever JSON can be sent and received.

What makes Telepact different? It takes the differentiating features of the
industry's most popular API technologies, and combines them together through 3
key innovations:

1. **JSON as a Query Language** - API calls and `SELECT`-style queries are all
   achieved with JSON abstractions, giving first-class status to clients
   wielding only a JSON library
2. **Binary without code generation** - Binary protocols are established through
   runtime handshakes, rather than build-time code generation, offering binary
   efficiency to clients that want to avoid code generation toolchains
3. **Hypermedia without HTTP** - API calls can return functions with pre-filled
   arguments, approximating a link that can be followed, all achieved with pure
   JSON abstractions

These innovations allow Telepact to design for the minimalist consumer while
giving clients the option to enrich the consumer experience by:
- Selecting less fields to reduce response sizes
- Using schema-backed mocks to validate integrations before switching to live servers
- Generating code when stronger static ergonomics are worth the extra tooling
- Using binary serialization to reduce request/response sizes

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
