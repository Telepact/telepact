# Home

Welcome to the Telepact docs. Use this page to find the right path based on
what you are trying to do: learn the basics, design a schema, build clients and
servers, or operate a Telepact API in production.

## Start here

- [Quickstart](./example.md) for the fastest end-to-end example
- [Learn Telepact by Example](./01-learn-by-example/README.md) for a guided tour
- [Demos](./demos.md) for runnable focused examples

## Common paths

### I want the fastest quickstart

- [Quickstart](./example.md)
- [Learn Telepact by Example](./01-learn-by-example/README.md)

### I want browser or Node clients

- [Client Paths](./03-build-clients-and-servers/02-client-paths.md) to choose between plain JSON, the client
  library, and generated code
- [Transport Guide](./03-build-clients-and-servers/01-transports.md) for browser `fetch`, WebSocket, and server
  transport wiring
- [TypeScript library README](../lib/ts/README.md) for runtime API usage

### I want auth guidance

- [Production Guide](./04-operate/01-production-guide.md#3-auth-and-observability-patterns) for the recommended
  production auth boundary
- [Learn by Example: Auth](./01-learn-by-example/05-auth/18-auth.md) for the `@auth_` convention from the client
  side
- [Cookie auth example](../example/py-http-cookie-auth/README.md) for a minimal transport-to-`@auth_` example

### I want production guidance

- [Production Guide](./04-operate/01-production-guide.md)
- [Runtime Error Guide](./04-operate/02-runtime-errors.md)
- [Versions](./04-operate/03-versions.md)

### I want tooling or code generation

- [Tooling Workflow](./03-build-clients-and-servers/04-tooling-workflow.md)
- [Learn by Example: Code generation](./01-learn-by-example/07-code-generation/21-code-generation.md)
- [Telepact CLI](../sdk/cli/README.md)
- [Browser Console](../sdk/console/README.md)

### I want runnable examples

- [Demos](./demos.md)
- [Example directory index](../example/README.md)

## Design APIs

- [Schema Writing Guide](./02-design-apis/01-schema-guide.md) for the full schema language
- [Core Concepts](./02-design-apis/02-core-concepts.md) for Telepact's message model, schema
  role, headers, links, select, and binary at a high level
- [Extensions](./02-design-apis/03-extensions.md) for Telepact's reserved `_ext.*_` types
- [JSON Schema](../common/json-schema.json) for schema-file validation

## Build clients and servers

- [Transport Guide](./03-build-clients-and-servers/01-transports.md) for HTTP and WebSocket wiring patterns
- [Client Paths](./03-build-clients-and-servers/02-client-paths.md) for choosing between plain JSON, client
  libraries, and generated code
- [Server Paths](./03-build-clients-and-servers/03-server-paths.md) for choosing a runtime and wiring a server
- [Tooling Workflow](./03-build-clients-and-servers/04-tooling-workflow.md) for `fetch`, `compare`, `mock`, and
  `codegen`

### Libraries

- [TypeScript](../lib/ts/README.md)
- [Python](../lib/py/README.md)
- [Java](../lib/java/README.md)
- [Go](../lib/go/README.md)

### SDK tools

- [CLI](../sdk/cli/README.md)
    - Fetch schemas, compare versions, mock APIs, and generate code from the
      command line
- [Browser Console](../sdk/console/README.md)
    - Browse docs and submit live requests against a running Telepact server
- [Prettier Plugin](../sdk/prettier/README.md)
    - Format checked-in Telepact schema files consistently

## Operate

- [Production Guide](./04-operate/01-production-guide.md) for rollout, auth, compatibility,
  and observability guidance
- [Runtime Error Guide](./04-operate/02-runtime-errors.md) for local/runtime debugging
- [Versions](./04-operate/03-versions.md) for the latest published library and SDK versions

## Background and reference

- [FAQ](./05-background-and-reference/01-faq.md) for Telepact's more unusual design decisions
- [Motivation](./05-background-and-reference/02-motivation.md) for the ecosystem goals and tradeoffs
