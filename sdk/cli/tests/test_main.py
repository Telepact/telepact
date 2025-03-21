#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import pytest
from click.testing import CliRunner
# Adjust the import path according to your project structure
from telepact_cli.cli import main
import traceback


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_command_java(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ['codegen', '--schema-dir', 'tests/data', '--lang', 'java', '--out', 'tests/output/java', '--package', 'output'])

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
    # TODO: implement this part


def test_command_py(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ['codegen', '--schema-dir', 'tests/data', '--lang', 'py', '--out', 'tests/output/py'])

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
    # TODO: implement this part


def test_command_ts(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ['codegen', '--schema-dir', 'tests/data', '--lang', 'ts', '--out', 'tests/output/ts'])

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
    # TODO: implement this part
