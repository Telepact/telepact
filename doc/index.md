# Home

Welcome to the Telepact docs. Use this page to find the right path based on
what you are trying to do: learn the basics, design a schema, build clients and
servers, or operate a Telepact API in production.

## Start Here

- [Quickstart](./example.md) for the fastest end-to-end example
- [Learn Telepact by Example](./learn-by-example/README.md) for a guided tour
- [Demos](../example/README.md) for runnable end-to-end examples

## Design APIs

- [Schema Writing Guide](./schema-guide.md) for the full schema language
- [Core Concepts](./core-concepts.md) for Telepact's message model, schema
  role, headers, links, select, and binary at a high level
- [Extensions](./extensions.md) for Telepact's reserved `_ext.*_` types
- [JSON Schema](../common/json-schema.json) for schema-file validation

## Build Clients & Servers

- [Transport Guide](./transports.md) for HTTP and WebSocket wiring patterns
- [Client Paths](./client-paths.md) for choosing between plain JSON, client
  libraries, and generated code
- [Server Paths](./server-paths.md) for choosing a runtime and wiring a server
- [Tooling Workflow](./tooling-workflow.md) for `fetch`, `compare`, `mock`, and
  `codegen`

### Libraries

- [TypeScript](../lib/ts/README.md)
- [Python](../lib/py/README.md)
- [Java](../lib/java/README.md)
- [Go](../lib/go/README.md)

### SDK Tools

- [CLI](../sdk/cli/README.md)
    - Fetch schemas, compare versions, mock APIs, and generate code from the
      command line
- [Browser Console](../sdk/console/README.md)
    - Browse docs and submit live requests against a running Telepact server
- [Prettier Plugin](../sdk/prettier/README.md)
    - Format checked-in Telepact schema files consistently

## Operate

- [Production Guide](./production-guide.md) for rollout, auth, compatibility,
  and observability guidance
- [Runtime Error Guide](./runtime-errors.md) for local/runtime debugging
- [Versions](./versions.md) for the latest published library and SDK versions

## Background & Reference

- [FAQ](./faq.md) for Telepact's more unusual design decisions
- [Motivation](./motivation.md) for the ecosystem goals and tradeoffs
