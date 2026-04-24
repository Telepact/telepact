# Introduction

Telepact is a thin but powerful RPC framework built on JSON.

Why choose Telepact:

- ✨ **Plain JSON is the default** - Clients never need to worry about
  Telepact libraries or generated code. Tool optionality is real, not theoretical.
- 🎯 **JSON as a Query Language** - No need to invent a second query language.
  Telepact has simple built-in options to trim responses according to client needs.
- ⚡ **Binary without the toolchain tax** - Have you ever seen a binary protocol
  that didn't require code generation? Now you have, with Telepact.
    - (This innovation was made possible with MessagePack ❤️)
- 🔗 **Hypermedia without HTTP** - API calls can return functions with pre-filled arguments.
  Who said links had to be urls?
- 🧪 **Schemas pull real weight** - The JSON-written Telepact schema holds the ecosystem
  together. API introspection super-charges your develpoment, with type validation,
  docs, mocks, and even generate your own code bindings.

Modern innovations, without the ceremony 🚀

# It's just JSON at the core
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
