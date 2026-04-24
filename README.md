# Introduction

Telepact is an RPC framework for people who want modern API power without the
usual ceremony ✨

It starts with plain JSON, then quietly layers in the kind of capabilities that
normally drag along bespoke clients, code generation pipelines, or heavyweight
protocols. The result is an API model that feels refreshingly simple on day one
and surprisingly high-performance as you scale 🚀

What makes Telepact feel different is that it fuses some of the best ideas from
today's most compelling API styles into 3 sharp innovations:

1. **JSON as a Query Language** - API calls and `SELECT`-style queries happen
   through JSON abstractions, so a client armed with nothing more than a JSON
   library still gets first-class capabilities
2. **Binary without code generation** - Binary protocols are negotiated at
   runtime instead of locked behind build-time code generation, giving you a
   path to efficiency without inheriting a toolchain
3. **Hypermedia without HTTP** - API calls can return functions with pre-filled
   arguments, approximating links you can follow, all through pure JSON
   abstractions

That means Telepact can stay friendly to the most minimalist consumer while
still unlocking serious upgrades when you want them:
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
