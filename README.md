# Introduction

Telepact is an API ecosystem for bridging programs across inter-process
communication boundaries.

For further reading, see [Motivation](./doc/motivation.md).

For explanations of various design decisions, see [the FAQ](./doc/faq.md).

## At a glance

```
<< [{},{"fn.add": {"x": 1,"y": 2}}]
>> [{},{"Ok_": {"result": 3}}]
```

# Development

The Telepact project is structed as a monorepo.

- `common` - files commonly used across the Telepact ecosystem
- `bind` - contains lightweight wrapper libraries that use bindings to
   expose a formal Telepact implementation in a language not yet targetted by
   a formal Telepact implementation.
- `lib` - contains all formal library implementations of Telepact in various
   programming languages
- `test` - contains the test framework that enforces the Telepact specification
   on all implementations found in `lib`
- `sdk` - contains various programs that assist developing in the Telepact
   ecosystem
- `tool` - contains various programs that assist the development of the
   Telepact project

# Licensing
Telepact is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for 
the full license text. See [NOTICE](NOTICE) for additional information regarding 
copyright ownership.
