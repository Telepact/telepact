# Telepact

Telepact is an API ecosystem for synchronous inter-process communication. It aims to make it easy to set up client-server semantics across IPC boundaries.

## Motivation

The state of automated software QA is not great. The utility of CI tests depends on the stability of the interfaces they interact with, but many IPC boundary technologies make tradeoffs that reduce long-term trust and maintainability. Modern API technologies such as REST, gRPC, and GraphQL each optimize heavily for specific goals while compromising other important qualities like predictability, portability, or ergonomics. As a result, developers often build tests against unstable implementation details instead of stable interfaces, which reduces the longevity and reliability of automated tests.

Telepact is an attempt to improve the stability and usability of IPC interfaces so that automated QA can more reliably depend on them. The goal is to make stable IPC contracts practical and ergonomic enough that developers are comfortable building long-lived tests against them.

## Values

Telepact prioritizes strong interface descriptions and toolchain-free ergonomics. When interfaces can be described accurately in a portable manner, trust and interoperability improve across the developer ecosystem. When the toolchain-free experience (for example, JSON) is treated as a first-class workflow, accessibility improves as well. Existing API technologies often compromise one or both of these values.

gRPC prioritizes binary efficiency, but this often comes with code-generation-heavy toolchains, and its JSON proxy support lacks the ergonomics of a first-class design.

REST prioritizes compatibility and convention, but developers are frequently left working with loosely typed URL abstractions, and JSON Schema alone does not fully standardize patterns or improve type safety.

GraphQL prioritizes client ergonomics, but this can introduce unpredictable server-side performance and security considerations, while still relying heavily on string-based query semantics.

Telepact starts with a reliable interface description schema, including rich but non-redundant typing abstractions, and builds features from there. A strong schema foundation enables capabilities such as schema-powered mocks while preserving a JSON-first API experience.

## Guidelines

Keep all core runtimes in `lib/` as tight implementation mirrors of one another. They should all support the same Telepact specification and follow predictable file and folder patterns.

Keep Telepact runtime testing in `test/`, not in `lib/`. All runtimes should be held to the same standard to prevent behavior drift, so a shared test harness applied equally to each runtime implementation best ensures consistency.
