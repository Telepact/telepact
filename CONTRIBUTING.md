# Contributing

## Folder Structure

The Telepact project is structured as a monorepo.

-   `common` - files commonly used across the Telepact ecosystem
-   `bind` - contains lightweight wrapper libraries that use bindings to expose
    a formal Telepact implementation in a language not yet targeted by a formal
    Telepact implementation.
-   `lib` - contains all formal library implementations of Telepact in various
    programming languages
-   `test` - contains the test framework that enforces the Telepact
    specification on all implementations found in `lib`
-   `sdk` - contains various programs that assist developing in the Telepact
    ecosystem
-   `tool` - contains various programs that assist the development of the
    Telepact project

## Building and Testing

There are several top-level `Makefile` commands for building and testing the
various subprojects.

Example:

```
make java
make test-java
make clean-java
```

Most of these commands simply delegate to a `Makefile` in the related
subproject. In some cases, it may be simpler to change your working directory to
the related subproject for greater control over the build tools in that
subproject.

## Developer Workflow

The entire project uses a hierarchical `Makefile` system. The root `Makefile`
delegates tasks to the `Makefile`s within each component's directory.

### Building

- To build a specific library, navigate to its directory or use the root
  makefile. For example, to build the Java library:

  ```sh
  make java
  # or
  cd lib/java && make
  ```

- Similarly for other components: `make ts`, `make py`, `make cli`, etc.

### Testing

- Run tests from the `/test/runner` directory:

  ```sh
  uv run python -m pytest -s -vv -k <test_name>
  ```

- NOTE: You need the `-s` flag to show all request/response payloads for
  debugging. However, avoid using `-s` when `-k` is not specified, as it will
  produce excessive output.

- The `test/runner` suite uses per-language test consumers in
  `test/lib/{go,java,py,ts}`. Those directories often install or package
  artifacts built from `lib/{lang}`, so they are not always reading
  `lib/{lang}` source files directly at test time.

- If you change `lib/<lang>`, prefer running the matching root target such as
  `make test-py`, `make test-ts`, `make test-java`, or `make test-go` before
  trusting `test/runner` results. These targets rebuild the library artifact,
  refresh the corresponding `test/lib/<lang>` consumer, and then run the
  matching runner shard.

- If you only need to refresh the per-language test consumer without running
  pytest, use `make prepare-test-py`, `make prepare-test-ts`,
  `make prepare-test-java`, or `make prepare-test-go`.

- If you only need to run the matching runner shard without rebuilding the
  consumer first, use `make test-py-run`, `make test-ts-run`,
  `make test-java-run`, or `make test-go-run`.

- If test environments may be stale, run `make clean-test` first, then rerun
  the appropriate `make test-<lang>` target.

- Be careful running `uv run python -m pytest ...` directly in `test/runner`
  after a library change. That is only reliable if the corresponding
  `test/lib/<lang>` consumer has already been rebuilt.

- Do not create tests in `lib/` or in `test/lib`. All test cases should be
  defined in `test/runner`, and test harnesses in `test/lib`.

### Final Verification

- If you have made changes to `lib/`, it is a good idea to run `make local-ci`
  from the repository root. This target cleans the shared workspace, rebuilds
  the primary CI targets in order, and catches issues that only show up when
  the repo is exercised end-to-end in one environment.
