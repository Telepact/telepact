import pytest
from click.testing import CliRunner
# Adjust the import path according to your project structure
from uapicodegen.gen import generate
import traceback


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_command_java(runner: CliRunner) -> None:
    result = runner.invoke(
        generate, ['--schema', 'tests/data/example1.uapi.json', '--lang', 'java', '--out', 'tests/output/java', '--package', 'output'])

    # print stack trace
    import traceback

    # Assuming result.exc_info is a tuple (exc_type, exc_value, exc_traceback)
    if result.exc_info:
        # Format the traceback and print it
        traceback_str = ''.join(traceback.format_exception(*result.exc_info))
        print(traceback_str)

    print(f'Output: {result.output}')

    assert result.exit_code == 0

    # open the generated file and check if it contains the expected content
    # todo: implement this part


def test_command_py(runner: CliRunner) -> None:
    result = runner.invoke(
        generate, ['--schema', 'tests/data/example1.uapi.json', '--lang', 'py', '--out', 'tests/output/py'])

    # print stack trace
    import traceback

    # Assuming result.exc_info is a tuple (exc_type, exc_value, exc_traceback)
    if result.exc_info:
        # Format the traceback and print it
        traceback_str = ''.join(traceback.format_exception(*result.exc_info))
        print(traceback_str)

    print(f'Output: {result.output}')

    assert result.exit_code == 0

    # open the generated file and check if it contains the expected content
    # todo: implement this part
