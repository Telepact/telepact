import pytest
from click.testing import CliRunner
# Adjust the import path according to your project structure
from uapicodegen.main import main
import traceback


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_command(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ['--schema', 'tests/data/example1.uapi.json', '--lang', 'java', '--out', 'tests/output'])

    # print stack trace
    import traceback

    # Assuming result.exc_info is a tuple (exc_type, exc_value, exc_traceback)
    if result.exc_info:
        # Format the traceback and print it
        traceback_str = ''.join(traceback.format_exception(*result.exc_info))
        print(traceback_str)

    assert result.exit_code == 0

    # open the generated file and check if it contains the expected content
    # todo: implement this part
