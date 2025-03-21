# Introduction

Telepact is an API ecosystem fueled by messages.

It follows 4 principles:
1. **Accessibility** - Whether you're bringing sophisticated toolchains or a
   minimialist setup, you can easily participate in Telepact with the
   complexity-level you need, from plain json to generated code with efficient
   binary serialization.
2. **Portability** - Telepact definitions take the form of currency in the
   Telepact ecosystem, unlocking powerful "based on" features such as
   documentation rendering, code completion, mocking, and code generation.
3. **Trust** - Features are governed not by server implementations, but rather
   by the Telepact ecosystem itself; consequently, clients can confidently
   integrate with all Telepact servers with robust expectations.
4. **Stability** - Telepact's interface description language offers a powerful
   but carefully curated list of paradigms to ensure API designs don't fall
   victim to common API evolution pitfalls.

For further reading, see [Motivation](./doc/motivation.md).

For explanations of various design decisions, see [the FAQ](./doc/faq.md).

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
