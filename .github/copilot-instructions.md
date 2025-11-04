# Telepact AI Coding Conventions

This document provides guidance for AI agents working within the Telepact codebase.

## Big Picture

Telepact is a multi-language API ecosystem built around a unified schema definition. The core idea is to define your API in `.telepact.json` files, and then use language-specific libraries to implement clients and servers.

The project is a monorepo containing several independent but related components:
-   **Core Libraries (`/lib`)**: Implementations of the Telepact protocol in `go`, `java`, `py` (Python), and `ts` (TypeScript). These provide the `Server` and `Client` classes.
-   **SDKs (`/sdk`)**: Tools built on top of the core libraries, including a `cli`, a web-based `console`, and a `prettier` plugin for formatting schema files.
-   **Bindings (`/bind`)**: Language-specific bindings, like for `dart`.
-   **Schema Definitions**: APIs are defined in `.telepact.json` files (e.g., `common/auth.telepact.json`). These files are the source of truth for all API interactions.

The key architectural pattern is that the core libraries are transport-agnostic. They provide a `process` (server) or `adapter` (client) function that deals with raw byte arrays or messages, allowing you to wire them into any transport layer (HTTP, WebSockets, etc.).

## Developer Workflow

The entire project uses a hierarchical `Makefile` system. The root `Makefile` delegates tasks to the `Makefile`s within each component's directory.

### Building

-   To build a specific library, navigate to its directory or use the root makefile. For example, to build the Java library:
    ```sh
    make java
    # or
    cd lib/java && make
    ```
-   Similarly for other components: `make ts`, `make py`, `make cli`, etc.

### Testing

-   Run tests from the `/test/runner` directory:
    ```sh
    poetry run python -m pytest -s -vv -k <test_name>
    ```

-   NOTE: You need the `-s` flag to show all request/response payloads for debugging.
    HOWEVER, avoid using `-s` when `-k` is not specified, as it will produce excessive output.

### Key Files & Directories

-   `Makefile`: The entry point for all build, test, and deploy operations.
-   `lib/{go,java,py,ts}`: The core libraries. Changes here impact the fundamental behavior of Telepact.
-   `bind/dart`: Language-specific bindings for Dart.
-   `test/runner`: The cross-language integration test suite. This is the best place to understand how different language implementations are expected to behave and interact.
-   `common/*.telepact.json`: The common schema files that define the internal APIs used by Telepact itself.
-   `sdk/console`: A SvelteKit and TypeScript project for the developer console.
-   `sdk/cli`: A Python/Poetry project for the command-line interface.
-   `sdk/prettier`: A project for the Prettier plugin.

## Schema Authoring (`.telepact.json`)

Telepact schemas are defined in `.telepact.json` files. These files are the single source of truth for API definitions. A schema is a JSON array of definitions. The full guide can be found in `doc/schema-guide.md`.