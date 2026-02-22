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

# JSON in, JSON out

Schema:
```json
[{"fn.helloWorld": {}, "->": [{"Ok_": {"msg": "string"}}]}]
```
Request:
```json
[{}, {"fn.helloWorld":{}}]
```
Response:
```json
[{}, {"Ok_": {"msg": "Hello world!"}}]
```

Check out the [full-stack example](./doc/example.md).

# Explore

To learn how to write Telepact APIs, see the [API Schema Guide](./doc/schema-guide.md).
A [JSON Schema](./common/json-schema.json) is available for validation.

To learn how to serve a Telepact API, see the specific library docs:
- [Typescript](./lib/ts/README.md)
- [Python](./lib/py/README.md)
- [Java](./lib/java/README.md)
- [Go](./lib/go/README.md)

For development assistance, see the SDK tool docs:
- [CLI](./sdk/cli/README.md)
    - Conveniently retreive API schemas from running live Telepact servers, and
      use schemas to create mock servers and generate code bindings, all from
      the command line
- [Browser Console](./sdk/console/README.md)
    - Develop against a live Telepact server by reading rendered docs, drafting
      requests, and submitting live requests with json-friendly editors
- [Prettier Plugin](./sdk/prettier/README.md)
    - Consistently format your Telepact api schemas, especially the doc-strings


For further reading, see [Motivation](./doc/motivation.md).

For explanations of various design decisions, see [the FAQ](./doc/faq.md).

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE) for the full license text. See [NOTICE](NOTICE) for
additional information regarding copyright ownership.
