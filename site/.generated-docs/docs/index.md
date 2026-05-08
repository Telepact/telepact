# Documentation

Welcome to the Telepact docs. Use this page to find the right path based on
what you are trying to do: learn the basics, design a schema, build clients and
servers, or place Telepact inside a larger service.

## Start here

- [Quickstart](concepts.md#quickstart) for the fastest end-to-end example
- [Learn Telepact by Example](learn-by-example.md) for a guided tour
- [Demos](examples.md) for runnable end-to-end examples

## Common paths

- **I want the quickest possible start**
  - [Quickstart](concepts.md#quickstart)
  - Then [Learn Telepact by Example](learn-by-example.md)
- **I want browser + Node usage**
  - [Transport Guide](concepts.md#transport-guide) for browser TypeScript + `fetch` and WebSocket patterns
  - [Client Paths](concepts.md#client-paths) for choosing between plain JSON, runtime libraries, schema-backed mocks, and optional generated code
  - [TypeScript library README](lib-and-sdk-survey.md#typescript) for the runtime client/server API
- **I want an end-to-end browser example**
  - [`example/full-stack`](examples/full-stack.md) for a browser TypeScript frontend + Python backend with Playwright end-to-end coverage
- **I want schema-backed integration confidence**
  - [Tooling Workflow](concepts.md#tooling-workflow) for the fetch/compare/mock/codegen workflow
  - [Learn by Example: Mock server](learn-by-example.md#14-mock-server)
  - [Learn by Example: Verify](learn-by-example.md#17-verify)
- **I need auth**
  - [Auth Guide](concepts.md#auth-guide) for Telepact's canonical auth convention
  - [`example/py-http-cookie-auth`](examples/py-http-cookie-auth.md) for one browser/session-cookie example
- **I need operating-boundary guidance**
  - [Operating Boundary Guide](concepts.md#operating-boundary-guide)
  - [Runtime Error Guide](concepts.md#runtime-error-guide)
- **I need tooling or optional code generation**
  - [Tooling Workflow](concepts.md#tooling-workflow)
  - [CLI](lib-and-sdk-survey.md#cli)
  - [Learn by Example: Code generation](learn-by-example.md#21-code-generation)
- **I want runnable examples**
  - [Demos](examples.md)
  - [Transport Guide](concepts.md#transport-guide) for the guide-to-demo mapping

## Design APIs

- [Schema Writing Guide](concepts.md#schema-writing-guide) for the full schema language
- [Core Concepts](concepts.md#core-concepts) for Telepact's message model, schema
  role, headers, links, select, and binary at a high level
- [Extensions overview](concepts.md#extensions) for Telepact's reserved `_ext.*_` types
- [`_ext.Select_`](concepts.md#ext-select) for response selection
- [Mock extensions](concepts.md#mock-extensions) for `_ext.Call_` and `_ext.Stub_`
- [JSON Schema](/common/json-schema.json) for schema-file validation

## Build clients and servers

- [Transport Guide](concepts.md#transport-guide) for HTTP and WebSocket wiring patterns
- [Client Paths](concepts.md#client-paths) for choosing between plain JSON, client
  libraries, schema-backed mocks, and optional generated code
- [Server Paths](concepts.md#server-paths) for choosing a runtime and wiring a server
- [Auth Guide](concepts.md#auth-guide) for Telepact's canonical auth convention
- [Tooling Workflow](concepts.md#tooling-workflow) for `fetch`, `compare`, `mock`, and
  `codegen`

### Libraries

- [TypeScript](lib-and-sdk-survey.md#typescript)
- [Python](lib-and-sdk-survey.md#python)
- [Java](lib-and-sdk-survey.md#java)
- [Go](lib-and-sdk-survey.md#go)

### SDK tools

- [CLI](lib-and-sdk-survey.md#cli)
    - Fetch schemas, compare versions, run schema-backed mocks, and optionally
      generate code from the command line
- [Browser Console](lib-and-sdk-survey.md#console)
    - Browse docs and submit live requests against a running Telepact server
- [Prettier Plugin](lib-and-sdk-survey.md#prettier-plugin)
    - Format checked-in Telepact schema files consistently

## Operate

- [Operating Boundary Guide](concepts.md#operating-boundary-guide) for Telepact-specific auth,
  compatibility, and observability boundaries
- [Runtime Error Guide](concepts.md#runtime-error-guide) for local/runtime debugging

## Background and reference

- [FAQ](concepts.md#faq) for Telepact's more unusual design decisions
- [Motivation](concepts.md#motivation) for the ecosystem goals and tradeoffs
