# Agent Instructions

This document provides guidance for AI agents working within the Telepact codebase.

## Big Picture

Telepact is a multi-language API ecosystem built around a unified schema definition. The core idea is to define your API in `.telepact.yaml` files for normal authoring, and then use language-specific libraries to implement clients and servers. `.telepact.json` remains valid and is still the lowered, wire-aligned form.

The project is a monorepo containing several independent but related components:
-   **Core Libraries (`/lib`)**: Implementations of the Telepact protocol in `go`, `java`, `py` (Python), and `ts` (TypeScript). These provide the `Server` and `Client` classes.
-   **SDKs (`/sdk`)**: Tools built on top of the core libraries, including a `cli`, a web-based `console`, and a `prettier` plugin for formatting schema files.
-   **Bindings (`/bind`)**: Language-specific bindings, like for `dart`.
-   **Schema Definitions**: APIs are usually authored in `.telepact.yaml` files (e.g., `common/auth.telepact.yaml`). `.telepact.json` is also accepted, but YAML is preferred at rest because multi-line docstrings are much cleaner there.

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
    uv run python -m pytest -s -vv -k <test_name>
    ```

-   NOTE: You need the `-s` flag to show all request/response payloads for debugging.
    HOWEVER, avoid using `-s` when `-k` is not specified, as it will produce excessive output.

-   The `test/runner` suite uses per-language test consumers in `test/lib/{go,java,py,ts}`.
    Those directories often install or package artifacts built from `lib/{lang}`, so they are not always reading `lib/{lang}` source files directly at test time.

-   If you change `lib/<lang>`, prefer running the matching root target such as `make test-py`, `make test-ts`, `make test-java`, or `make test-go` before trusting `test/runner` results.
    These targets rebuild the library artifact, refresh the corresponding `test/lib/<lang>` consumer, and then run the matching runner shard.

-   If you only need to refresh the per-language test consumer without running pytest, use `make prepare-test-py`, `make prepare-test-ts`, `make prepare-test-java`, or `make prepare-test-go`.

-   If you only need to run the matching runner shard without rebuilding the consumer first, use `make test-py-run`, `make test-ts-run`, `make test-java-run`, or `make test-go-run`.

-   If test environments may be stale, run `make clean-test` first, then rerun the appropriate `make test-<lang>` target.

-   Be careful running `uv run python -m pytest ...` directly in `test/runner` after a library change.
    That is only reliable if the corresponding `test/lib/<lang>` consumer has already been rebuilt.

### Key Files & Directories

-   `Makefile`: The entry point for all build, test, and deploy operations.
-   `lib/{go,java,py,ts}`: The core libraries. Changes here impact the fundamental behavior of Telepact.
-   `bind/dart`: Language-specific bindings for Dart.
-   `test/runner`: The cross-language integration test suite. This is the best place to understand how different language implementations are expected to behave and interact.
-   `common/*.telepact.yaml`: The common schema files that define the internal APIs used by Telepact itself.
-   `sdk/console`: A SvelteKit and TypeScript project for the developer console.
-   `sdk/cli`: A Python/uv project for the command-line interface.
-   `sdk/prettier`: A project for the Prettier plugin.

## Schema Authoring (`.telepact.yaml`)

Telepact schemas are usually authored in `.telepact.yaml` files. `.telepact.json` is also supported, but YAML is preferred for checked-in schemas because multi-line docstrings are much easier to read and edit. Semantically, the schema is still a JSON-shaped array of definitions, and the tooling lowers YAML to JSON internally. The full guide can be found in `doc/schema-guide.md`.

## Skills

Repo-local skills live under `skills/` and should be used when the task matches them closely.

### Available skills

-   `telepact-schema-writing`: Convert a plain-English API description into a correct Telepact schema, usually authored as `.telepact.yaml`. (file: `/Users/brendanbartels/workspace/telepact/skills/telepact-schema-writing/SKILL.md`)
-   `telepact-server`: Implement a Telepact server for an already-drafted schema using the Telepact server library in Go, Java, Python, or TypeScript. (file: `/Users/brendanbartels/workspace/telepact/skills/telepact-server/SKILL.md`)
-   `telepact-client`: Implement a Telepact client for an already-drafted schema using either raw Telepact JSON over a transport or the Telepact client library in Go, Java, Python, or TypeScript. (file: `/Users/brendanbartels/workspace/telepact/skills/telepact-client/SKILL.md`)
-   `telepact-downstream-testing`: Test code that consumes an external Telepact API by fetching the downstream schema and running a Telepact CLI mock server, with optional stubbing and request verification. (file: `/Users/brendanbartels/workspace/telepact/skills/telepact-downstream-testing/SKILL.md`)

### How to use skills

-   If the user names one of these skills, or the task clearly matches one, open its `SKILL.md` and follow it.
-   Keep context small: read only the skill plus the repo files needed for the active task.
-   If a skill does not fit cleanly, state that briefly and continue with the closest sensible approach.
