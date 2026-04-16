# Tooling Workflow

Telepact's tooling is designed around one artifact: the schema. The same
contract that powers runtime validation also powers fetching, comparison,
mocking, code generation, and interactive docs.

The recommended workflow is:

1. fetch or check in the schema you want to integrate against
2. compare schema revisions before releases
3. mock from that same schema while clients and tests are still in flight
4. generate bindings from that same schema when a supported language would
   benefit from a stronger typed API

That makes `fetch`, `compare`, `mock`, and `codegen` one loop instead of four
separate tools.

## 1. Fetch a schema

Use `telepact fetch` to retrieve a schema from a running Telepact server and
store it locally.

This is useful when you want to:

- inspect a live API contract
- save a checked-in schema for local development or CI
- feed the same schema into `compare`, `mock`, and `codegen`

Fetched schemas are especially useful when teams want one local artifact that
drives both contract review and generated bindings.

See:

- [Telepact CLI](../../sdk/cli/README.md)

## 2. Compare schema versions

Use `telepact compare` to check backwards compatibility between an old schema and
a new schema.

This is useful when you want to:

- gate schema changes in CI
- protect staggered rollouts
- make compatibility an explicit release check

In practice, compare usually runs on checked-in schemas that were previously
fetched from a live service or authored in the repo.

See:

- [Production Guide](../04-operate/01-production-guide.md)
- [Telepact CLI](../../sdk/cli/README.md)

## 3. Mock an API

Use `telepact mock` when clients need to develop before a live server is ready
or when tests need schema-valid responses on demand.

This is useful when you want to:

- unblock client development
- test against schema-valid responses
- add stubs and verification around expected calls

This is the bridge between schema review and application code: fetch the schema
once, then point your local tests and UI work at a schema-valid mock.

See:

- [Learn by Example: Mock server](../01-learn-by-example/04-mocking-an-integration/14-mock-server.md)
- [Learn by Example: Stock mock](../01-learn-by-example/04-mocking-an-integration/15-stock-mock.md)
- [Learn by Example: Stubs](../01-learn-by-example/04-mocking-an-integration/16-stubs.md)
- [Learn by Example: Verify](../01-learn-by-example/04-mocking-an-integration/17-verify.md)

## 4. Generate code

Use `telepact codegen` to generate bindings from a schema.

Use code generation when the schema is stable enough to share and the caller
would benefit from a more application-shaped API than raw `Message` objects.

This is especially useful when you want:

- stronger typing in supported languages
- generated request/response models
- less manual request boilerplate
- a generated client surface that stays in sync with a checked-in schema

See:

- [Learn by Example: Code generation](../01-learn-by-example/07-code-generation/21-code-generation.md)
- [Client Paths](./02-client-paths.md)
- [Telepact CLI](../../sdk/cli/README.md)

## Use the browser console

Use the [Telepact Console](../../sdk/console/README.md) when you want interactive
documentation, request drafting, and live requests against a running Telepact
server.
