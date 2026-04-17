# Agent Instructions

This document provides guidance for AI agents working within the Telepact codebase.

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

-   Do not create tests in `lib/` or in `test/lib`. All test cases should be defined in `test/runner`, and test harnesses in `test/lib`.

### Final Verification

-   If you have made changes to `lib/`, it is a good idea to run `make local-ci` from the repository root.
    This target cleans the shared workspace, rebuilds the primary CI targets in order, and catches issues that only show up when the repo is exercised end-to-end in one environment.

### Key Files & Directories

-   `Makefile`: The entry point for all build, test, and deploy operations.
-   `lib/{go,java,py,ts}`: The core libraries. Changes here impact the fundamental behavior of Telepact.
-   `bind/dart`: Language-specific bindings for Dart.
-   `test/runner`: The cross-language integration test suite. This is the best place to understand how different language implementations are expected to behave and interact.
-   `common/*.telepact.yaml`: The common schema files that define the internal APIs used by Telepact itself.
-   `sdk/console`: A React and Vite TypeScript project for the developer console.
-   `sdk/cli`: A Python/uv project for the command-line interface.
