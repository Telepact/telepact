# Home

Welcome to the Telepact docs. Use this page to find the right path based on
what you are trying to do: learn the basics, design a schema, build clients and
servers, or place Telepact inside a larger service.

## Start here

- [Quickstart](./example.md) for the fastest end-to-end example
- [Learn Telepact by Example](./learn-by-example/README.md) for a guided tour
- [Demos](../example/README.md) for runnable end-to-end examples

## Common paths

- **I want the quickest possible start**
  - [Quickstart](./example.md)
  - Then [Learn Telepact by Example](./learn-by-example/README.md)
- **I want browser + Node usage**
  - [Transport Guide](./build-clients-and-servers/transports.md) for browser TypeScript + `fetch` and WebSocket patterns
  - [Client Paths](./build-clients-and-servers/client-paths.md) for choosing between plain JSON, runtime libraries, schema-backed mocks, and optional generated code
  - [TypeScript library README](../lib/ts/README.md) for the runtime client/server API
- **I want an end-to-end browser example**
  - [`example/full-stack`](../example/full-stack/README.md) for a browser TypeScript frontend + Python backend with Playwright end-to-end coverage
- **I want schema-backed integration confidence**
  - [Tooling Workflow](./build-clients-and-servers/tooling-workflow.md) for the fetch/compare/mock/codegen workflow
  - [Learn by Example: Mock server](./learn-by-example/mocking-an-integration/mock-server.md)
  - [Learn by Example: Verify](./learn-by-example/mocking-an-integration/verify.md)
- **I need auth**
  - [Auth Guide](./build-clients-and-servers/auth.md) for Telepact's canonical auth convention
  - [`example/py-http-cookie-auth`](../example/py-http-cookie-auth/README.md) for one browser/session-cookie example
- **I need operating-boundary guidance**
  - [Operating Boundary Guide](./operate/production-guide.md)
  - [Runtime Error Guide](./operate/runtime-errors.md)
- **I need tooling or optional code generation**
  - [Tooling Workflow](./build-clients-and-servers/tooling-workflow.md)
  - [CLI](../sdk/cli/README.md)
  - [Learn by Example: Code generation](./learn-by-example/code-generation/code-generation.md)
- **I want runnable examples**
  - [Demos](../example/README.md)
  - [Transport Guide](./build-clients-and-servers/transports.md) for the guide-to-demo mapping

## Design APIs

- [Schema Writing Guide](./design-apis/schema-guide.md) for the full schema language
- [Core Concepts](./design-apis/core-concepts.md) for Telepact's message model, schema
  role, headers, links, select, and binary at a high level
- [Extensions overview](./design-apis/extensions.md) for Telepact's reserved `_ext.*_` types
- [`_ext.Select_`](./design-apis/select-extension.md) for response selection
- [Mock extensions](./design-apis/mock-extensions.md) for `_ext.Call_` and `_ext.Stub_`
- [JSON Schema](../common/json-schema.json) for schema-file validation

## Build clients and servers

- [Transport Guide](./build-clients-and-servers/transports.md) for HTTP and WebSocket wiring patterns
- [Client Paths](./build-clients-and-servers/client-paths.md) for choosing between plain JSON, client
  libraries, schema-backed mocks, and optional generated code
- [Server Paths](./build-clients-and-servers/server-paths.md) for choosing a runtime and wiring a server
- [Auth Guide](./build-clients-and-servers/auth.md) for Telepact's canonical auth convention
- [Tooling Workflow](./build-clients-and-servers/tooling-workflow.md) for `fetch`, `compare`, `mock`, and
  `codegen`

### Libraries

- [TypeScript](../lib/ts/README.md)
- [Python](../lib/py/README.md)
- [Java](../lib/java/README.md)
- [Go](../lib/go/README.md)

### SDK tools

- [CLI](../sdk/cli/README.md)
    - Fetch schemas, compare versions, run schema-backed mocks, and optionally
      generate code from the command line
- [Browser Console](../sdk/console/README.md)
    - Browse docs and submit live requests against a running Telepact server
- [Prettier Plugin](../sdk/prettier/README.md)
    - Format checked-in Telepact schema files consistently

## Operate

- [Operating Boundary Guide](./operate/production-guide.md) for Telepact-specific auth,
  compatibility, and observability boundaries
- [Runtime Error Guide](./operate/runtime-errors.md) for local/runtime debugging

## Background and reference

- [FAQ](./background-and-reference/faq.md) for Telepact's more unusual design decisions
- [Motivation](./background-and-reference/motivation.md) for the ecosystem goals and tradeoffs
