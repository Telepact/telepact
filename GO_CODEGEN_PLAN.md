# Background

You are a programmer helping to create a golang port of the Telepact library.
The main go library project is largely complete in `lib/go`, and most of the
tests are passing in `test/runner` (with the go test harness setup in `test/lib/go`).

Now you need to implement a go-lang code generation to the telepact cli in `sdk/cli`. A partial implemention is present, but it is not yet generating correct
output. You can reference cli logic for the other supported code-gen target languages like python and typescript.

# Goal

Your goal is to generate go-lang code by running `make test-cli` and inspecting
the generated results in `sdk/cli/tests/output`. The go-lang code results
should very comparable to the other programming languages, especially
typescript and python.