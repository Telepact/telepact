# Introduction

MsgPact is an API ecosystem driven by messages.

It is designed with 3 principles:
1. **Accessibility** - Whether you're bringing sophisticated toolchains or a
   minimialist setup, you can easily participate in MsgPact with the
   complexity-level you need, from plain json to generated code with efficient
   binary serialization.
2. **Trust** - Features are governed not by server implementations, but rather
   by the MsgPact ecosystem itself; consequently, clients can confidently
   integrate with all MsgPact servers with robust expectations.
3. **Stability** - MsgPact's interface description language offers a powerful
   but carefully curated list of paradigms to ensure API designs don't fall
   victim to common API evolution pitfalls.

For further reading, see [Motivation](./doc/motivation.md).

For explanations of various design decisions, see [the FAQ](./doc/faq.md).

# Development

The MsgPact project is structed as a monorepo.

- `common` - files commonly used across the MsgPact ecosystem
- `bind` - contains lightweight wrapper libraries that use bindings to
   expose a formal MsgPact implementation in a language not yet targetted by
   a formal MsgPact implementation.
- `lib` - contains all formal library implementations of MsgPact in various
   programming languages
   MsgPact library into a different programming language
- `test` - contains the test framework that enforces the MsgPact specification
   on all implementations found in `lib`
- `sdk` - contains various programs that assist developing with the MsgPact
   ecosystem
- `tool` - contains various programs meant to help the development of the
   MsgPact project

# Licensing
MsgPact is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full license text. See [NOTICE](NOTICE) for copyright information.
