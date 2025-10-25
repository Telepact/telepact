# Background

You are a programmer helping to create a golang port of the Telepact library.
The main go library project is largely complete in `lib/go`, and most of the
tests are passing in `test/runner` (with the go test harness setup in `test/lib/go`).

Now you need to add go-lang code generation to the telepact cli in `sdk/cli`. You
can reference the other supported languages there like python and typescript.

# Development Loop

To make changes that you can test, use the following procedure
1. Make changes in `sdk/cli`.
2. Build and install the new cli code with `make uninstall-cli clean-cli cli install-cli`
3. Clean and rebuild the test harness with `make clean-test test-trace-go`
4. Run a specific test in `test/runner` to verify if fix worked, such as `poetry run python -m pytest -k 'test_client_server_codegen_case[go-0]' -s -vv`.


# Goal

Your goal is to, from the `test/runner` directory, get `poetry run python -m pytest -k 'test_client_server_codegen_case[go'` to pass.

If a test fails when running the suite, DO NOT investigate right away.
The suite logs are too sparse. You MUST choose one of the tests that failed
and run that test individually to see the increased log output, such as
`poetry run python -m pytest -k 'test_client_server_codegen_case[go-0]' -s -vv`.

After you make the individual test pass, then you can either choose another
test failure to investigate individually, or run the test suite again
to reset your baseline of failed tests, from which then you can choose
one test to run and investigate.

Repeat until the whole test suite passes.