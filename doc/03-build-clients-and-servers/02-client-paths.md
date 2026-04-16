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

Available library docs:

- [TypeScript](../../lib/ts/README.md)
- [Python](../../lib/py/README.md)
- [Java](../../lib/java/README.md)
- [Go](../../lib/go/README.md)

This path works well when you want:

- a supported runtime library
- easier request/response handling
- a clearer adapter boundary around your transport
- to stay close to raw Telepact messages without writing the protocol from
  scratch

## Path 3: Generated client code

Use generated code when you want the strongest typing and the most ergonomic
application-level API for your target language.

This path works well when you want:

- compile-time feedback in supported languages
- stable generated bindings for a shared schema
- less hand-written request boilerplate
- generated request and response models that match your checked-in schema

This is usually the right choice when:

- the same schema is reused across multiple applications
- your TypeScript or Python code would benefit from compile-time guidance
- you want to commit generated bindings and update them as part of schema review

Start here:

- [Learn by Example: Code generation](../01-learn-by-example/07-code-generation/21-code-generation.md)
- [Tooling Workflow](./04-tooling-workflow.md)
- [Telepact CLI](../../sdk/cli/README.md)

## Manual client vs generated bindings

TypeScript is a good example of the tradeoff.

With the runtime library alone, you construct `Message` objects yourself:

```ts
const request = new Message({}, { "fn.add": { x: 2, y: 3 } });
const response = await client.request(request);
```

With generated bindings layered on top of that same runtime client, you get a
typed API shaped around your schema:

```ts
const typedClient = new TypedClient(client);
const response = await typedClient.add({}, add.Input.from({ x: 2, y: 3 }));
```

Both approaches use the same transport adapter and the same `telepact` runtime.
Generated bindings become compelling when the second form is easier to read,
harder to misuse, and worth checking in for the rest of your team.

## Choosing between them

Use plain JSON when simplicity matters most.

Use a library when you want the Telepact runtime to handle more of the protocol
details for you.

Use generated code when you want the most type-safe and ergonomic application
integration on top of a supported language runtime, especially when the schema
is shared broadly enough to justify checked-in bindings.

These paths are complementary rather than exclusive. Many teams start with
plain JSON or a library, then add generated code only for the callers that
benefit from it most.
