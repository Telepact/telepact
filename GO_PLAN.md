# Background

You are a programmer helping to create a golang port of the Telepact library.
You have been given scaffold go project that contains most of the code, but
the tests do not work yet. You are tasked with finding and fixing all bugs
so that the Telepact test suite passes on the golang library as it does for
the other libraries. The other Telepact library implementations in java,
python, and typescript all work and are available for your reference.

# Education

To understand what success looks like, from the `test/runner` directory, run:
`poetry run python -m pytest -k 'test_binary_client_server_case[py'`.

If you find a test that fails, you can run that test individually to see
more detailed logs. From the `test/runner` directory, run:
`poetry run python -m pytest -k 'test_binary_client_server_case[py-0]' -s -vv`.


# Goal

Your goal is to, from the `test/runner` directory, get `poetry run python -m pytest -k 'test_binary_client_server_case[go'` to pass.

If a test fails when running the suite, DO NOT investigate right away.
The suite logs are too sparse. You MUST choose one of the tests that failed
and run that test individually to see the increased log output, such as
`poetry run python -m pytest -k 'test_binary_client_server_case[go-0]' -s -vv`.

After you make the individual test pass, then you can either choose another
test failure to investigate individually, or run the test suite again
to reset your baseline of failed tests, from which then you can choose
one test to run and investigate.

Repeat until the whole test suite passes.