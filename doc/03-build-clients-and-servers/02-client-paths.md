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

For TypeScript/browser work, this is the right path for a first request, a docs
example, or a browser-console smoke test.

Start here:

- [Quickstart](../example.md)
- [Core Concepts](../02-design-apis/02-core-concepts.md)
- [Transport Guide](./01-transports.md)

## Path 2: Telepact client library

Use a Telepact client library when you want help with message construction,
serialization, validation-aware workflows, and binary negotiation.

Available library docs:

- [TypeScript](../../lib/ts/README.md)
- [Python](../../lib/py/README.md)
- [Java](../../lib/java/README.md)
- [Go](../../lib/go/README.md)

This path works well when you want:

- a supported runtime library
- easier request/response handling
- a clearer adapter boundary around your transport
- the recommended browser application path in TypeScript

## Path 3: Generated client code

Use generated code when you want the strongest typing and the most ergonomic
application-level API for your target language.

This path works well when you want:

- compile-time feedback in supported languages
- stable generated bindings for a shared schema
- less hand-written request boilerplate

Start here:

- [Learn by Example: Code generation](../01-learn-by-example/07-code-generation/21-code-generation.md)
- [Tooling Workflow](./04-tooling-workflow.md)
- [Telepact CLI](../../sdk/cli/README.md)

## Choosing between them

Use plain JSON when simplicity matters most.

Use a library when you want the Telepact runtime to handle more of the protocol
details for you.

Use generated code when you want the most type-safe and ergonomic application
integration on top of a supported language runtime.

## Recommended browser path for TypeScript teams

For most browser apps, the recommended progression is:

1. make the first call with plain JSON plus `fetch`
2. move to the TypeScript library with one small `fetch` adapter per endpoint
3. add generated bindings only after the schema becomes a shared contract

That gives you:

- a lightweight first-run experience
- a production-ready adapter boundary once the app is real
- stronger typing only when it starts paying for itself

Use the TypeScript library as the default browser integration when you want:

- transport code to stay limited to bytes in / bytes out
- schema-level response handling in normal app code
- negotiated binary and structured local error reporting

Start here:

- [TypeScript](../../lib/ts/README.md)
- [Transport Guide](./01-transports.md)
- [Runtime Error Guide](../04-operate/02-runtime-errors.md)

These paths are complementary rather than exclusive. Many teams start with
plain JSON or a library, then add generated code only for the callers that
benefit from it most.
