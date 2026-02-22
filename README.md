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
    - Conveniently run mock servers and fetch schemas all from the command line
- [Browser Console](./sdk/console/README.md)
    - Develop against a live Telepact server by reading rendered docs, drafting
      requests, and submitting live requests with json-friendly editors
- [Prettier Plugin](./sdk/prettier/README.md)
    - Consistently format your Telepact api schemas, especially the doc-strings

For a high-level understanding, see the [full-stack example](./doc/example.md).

For further reading, see [Motivation](./doc/motivation.md).

Telepact does have a few unorthodox design decisions. To be best informed,
you should read the explanations in [the FAQ](./doc/faq.md).

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE) for the full license text. See [NOTICE](NOTICE) for
additional information regarding copyright ownership.
