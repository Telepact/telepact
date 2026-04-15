# Tooling Workflow

Telepact's tooling is designed around the schema. The same contract that powers
runtime validation also powers fetching, comparison, mocking, code generation,
and interactive docs.

## Fetch a schema

Use the CLI to retrieve a schema from a running Telepact server and store it
locally.

This is useful when you want to:

- inspect a live API contract
- save a schema for local development
- feed the schema into other Telepact tools

See:

- [Telepact CLI](../../sdk/cli/README.md)

## Compare schema versions

Use `telepact compare` to check backwards compatibility between an old schema and
a new schema.

This is useful when you want to:

- gate schema changes in CI
- protect staggered rollouts
- make compatibility an explicit release check

See:

- [Production Guide](../05-operate/01-production-guide.md)
- [Telepact CLI](../../sdk/cli/README.md)

## Mock an API

Use `telepact mock` when clients need to develop before a live server is ready
or when tests need schema-valid responses on demand.

This is useful when you want to:

- unblock client development
- test against schema-valid responses
- add stubs and verification around expected calls

See:

- [Learn by Example: Mock server](../02-learn-by-example/04-mocking-an-integration/14-mock-server.md)
- [Learn by Example: Stock mock](../02-learn-by-example/04-mocking-an-integration/15-stock-mock.md)
- [Learn by Example: Stubs](../02-learn-by-example/04-mocking-an-integration/16-stubs.md)
- [Learn by Example: Verify](../02-learn-by-example/04-mocking-an-integration/17-verify.md)

## Generate code

Use `telepact codegen` to generate bindings from a schema.

This is useful when you want:

- stronger typing in supported languages
- generated request/response models
- less manual client boilerplate

See:

- [Learn by Example: Code generation](../02-learn-by-example/07-code-generation/21-code-generation.md)
- [Client Paths](../02-client-paths.md)
- [Telepact CLI](../../sdk/cli/README.md)

## Use the browser console

Use the [Telepact Console](../../sdk/console/README.md) when you want interactive
documentation, request drafting, and live requests against a running Telepact
server.
