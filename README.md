# Introduction

Telepact is an API ecosystem for bridging programs across inter-process
communication boundaries.

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
- Generating code to increase type safety
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

Start with the [docs landing page](./doc/index.md) for the full guide map.

Recommended paths:

- [Quickstart](./doc/example.md) for the fastest end-to-end path
- [Browser + Node usage](./doc/03-build-clients-and-servers/02-client-paths.md) for choosing between plain JSON,
  the TypeScript library, and generated clients
- [Auth guidance](./doc/04-operate/01-production-guide.md#3-auth-and-observability-patterns) for `@auth_`,
  middleware, and transport-boundary patterns
- [Production guidance](./doc/04-operate/01-production-guide.md) for rollout, compatibility, auth, and
  observability
- [Tooling and code generation](./doc/03-build-clients-and-servers/04-tooling-workflow.md) for `fetch`,
  `compare`, `mock`, `codegen`, and the browser console
- [Examples](./doc/demos.md) for runnable focused demos

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](./LICENSE) for the full license text. See [NOTICE](./NOTICE) for
additional information regarding copyright ownership.
