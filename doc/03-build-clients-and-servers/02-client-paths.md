# Client Paths

Telepact clients can participate at different levels of sophistication. Start
with the lightest path that fits your needs, then upgrade only where it helps.

## Path 1: Plain JSON client

The lightest client needs only:

- a JSON library
- a transport library
- knowledge of the Telepact message format

This path works well when you want:

- quick experiments
- shell scripts or browser fetch code
- a language that does not yet have a Telepact library
- the lowest possible tooling burden

Start here:

- [Quickstart](../example.md)
- [Core Concepts](../02-design-apis/02-core-concepts.md)
- [Transport Guide](./01-transports.md)

## Path 2: Telepact client library

Use a Telepact client library when you want help with message construction,
serialization, validation-aware workflows, and binary negotiation.

This is the best default path when you want more than raw JSON but do not want
to commit to generated bindings yet. Pair it with a Telepact mock when you want
schema-backed confidence that your integration will succeed before you point at
the live server.

Available library docs:

- [TypeScript](../../lib/ts/README.md)
- [Python](../../lib/py/README.md)
- [Java](../../lib/java/README.md)
- [Go](../../lib/go/README.md)

This path works well when you want:

- a supported runtime library
- easier request/response handling
- a clearer adapter boundary around your transport

## Path 3: Generated client code

Use generated code when you want the strongest typing and the most ergonomic
application-level API for your target language. This is an optional upgrade on
top of the runtime client path, not the required starting point.

This path works well when you want:

- compile-time feedback in supported languages
- stable generated bindings for a shared schema
- less hand-written request boilerplate
- an SDK-like API surface for humans, IDEs, and static analysis

Start here:

- [Learn by Example: Code generation](../01-learn-by-example/07-code-generation/21-code-generation.md)
- [Tooling Workflow](./04-tooling-workflow.md)
- [Telepact CLI](../../sdk/cli/README.md)

## Choosing between them

Use plain JSON when simplicity matters most.

Use a library when you want the Telepact runtime to handle more of the protocol
details for you.

Use a mock when you want to validate real requests against the schema, generate
schema-valid responses, and verify expected calls during integration work.

Use generated code when you want the most type-safe and ergonomic application
integration on top of a supported language runtime.

These paths are complementary rather than exclusive. Many teams start with
plain JSON or a library, use a mock for schema-backed confidence, then add
generated code only for the callers that benefit from stronger static
ergonomics.
