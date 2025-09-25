# Telepact AI Coding Conventions

This document provides guidance for AI agents working within the Telepact codebase.

## Big Picture

Telepact is a multi-language API ecosystem built around a unified schema definition. The core idea is to define your API in `.telepact.json` files, and then use language-specific libraries to implement clients and servers.

The project is a monorepo containing several independent but related components:
-   **Core Libraries (`/lib`)**: Implementations of the Telepact protocol in `java`, `py` (Python), and `ts` (TypeScript). These provide the `Server` and `Client` classes.
-   **SDKs (`/sdk`)**: Tools built on top of the core libraries, including a `cli`, a web-based `console`, and a `prettier` plugin for formatting schema files.
-   **Bindings (`/bind`)**: Language-specific bindings, like for `dart`.
-   **Schema Definitions**: APIs are defined in `.telepact.json` files (e.g., `common/auth.telepact.json`). These files are the source of truth for all API interactions.

The key architectural pattern is that the core libraries are transport-agnostic. They provide a `process` (server) or `adapter` (client) function that deals with raw byte arrays or messages, allowing you to wire them into any transport layer (HTTP, WebSockets, etc.).

## Developer Workflow

The entire project uses a hierarchical `Makefile` system. The root `Makefile` delegates tasks to the `Makefile`s within each component's directory.

### Building

-   To build everything: `make` (though this is often not necessary).
-   To build a specific library, navigate to its directory or use the root makefile. For example, to build the Java library:
    ```sh
    make java
    # or
    cd lib/java && make
    ```
-   Similarly for other components: `make ts`, `make py`, `make cli`, etc.

### Testing

The central test runner is located in `/test/runner`, which is a Python project. It is responsible for orchestrating tests across all language libraries to ensure they are interoperable.

-   To run all tests:
    ```sh
    make test
    ```
-   To run tests for a specific language:
    ```sh
    make test-java
    make test-py
    make test-ts
    ```
-   When in the `/test/runner` directory, you can run tests directly with `poetry run python -m pytest`.

-   To run a single test case (e.g., for debugging), use `pytest`'s `-k` option to select a test by name. The `test/runner/Makefile` has `test-trace-*` targets that are good examples:
    ```sh
    # From the root directory
    make test-trace-java

    # Or, from the test/runner directory
    poetry run python -m pytest -k test_client_server_case[java-0] -s -vv
    ```

### Key Files & Directories

-   `Makefile`: The entry point for all build, test, and deploy operations.
-   `lib/{java,py,ts}`: The core libraries. Changes here impact the fundamental behavior of Telepact.
-   `bind/dart`: Language-specific bindings for Dart.
-   `test/runner`: The cross-language integration test suite. This is the best place to understand how different language implementations are expected to behave and interact.
-   `common/*.telepact.json`: The common schema files that define the internal APIs used by Telepact itself.
-   `sdk/console`: A SvelteKit and TypeScript project for the developer console.
-   `sdk/cli`: A Python/Poetry project for the command-line interface.
-   `sdk/prettier`: A project for the Prettier plugin.
