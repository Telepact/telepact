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

from typing import Generator
import pytest
from click.testing import CliRunner
# Adjust the import path according to your project structure
from telepact_cli.cli import main
import traceback
import subprocess
import requests
import json
import time


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture(autouse=True, scope='function')
def tmp_dir_manager() -> Generator[None]:
    import os
    import shutil

    tmp_dir = 'tests/tmp'
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    yield

    # Cleanup after tests
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def test_demo_server() -> None:
    p = subprocess.Popen(['poetry', 'run', 'telepact', 'demo-server'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd='tests/tmp')

    try:
        # Check if the server is running
        time.sleep(1)
        response = requests.post('http://localhost:8000/api', data=json.dumps([{}, {'fn.ping_': {}}]))
        assert response.status_code == 200
        assert response.json() == [{}, {'Ok_': {}}]

        # Assert that we can fetch the schema using the cli
        result = subprocess.run(['poetry', 'run', 'telepact', 'fetch', '--http-url', 'http://localhost:8000/api', '--output-dir', 'api'], capture_output=True, text=True, cwd='tests/tmp')

        assert result.returncode == 0, f"Schema command failed with output: {result.stdout} and error: {result.stderr}"

        schema_file_path = 'tests/tmp/api/api.telepact.json'
        with open(schema_file_path, 'r') as schema_file:
            schema_content = schema_file.read()
            schema_json = json.loads(schema_content)

        reference_json = [{'///': ' A calculator app that provides basic math computation capabilities. ', 'info.Calculator': {}}, {'///': ' A function that adds two numbers. ', 'fn.add': {'x': ['number'], 'y': ['number']}, '->': [{'Ok_': {'result': ['number']}}]}, {'///': ' Compute the `result` of the given `x` and `y` values. ', 'fn.compute': {'x': ['union.Value'], 'y': ['union.Value'], 'op': ['union.Operation']}, '->': [{'Ok_': {'result': ['number']}}, {'ErrorCannotDivideByZero': {}}]}, {'///': ' Export all saved variables, up to an optional `limit`. ', 'fn.exportVariables': {'limit!': ['integer']}, '->': [{'Ok_': {'variables': ['array', ['struct.Variable']]}}]}, {'///': ' A function template. ', 'fn.getPaperTape': {}, '->': [{'Ok_': {'tape': ['array', ['struct.Computation']]}}]}, {'///': ' Save a set of variables as a dynamic map of variable names to their value. ', 'fn.saveVariables': {'variables': ['object', ['number']]}, '->': [{'Ok_': {}}]}, {'fn.showExample': {}, '->': [{'Ok_': {'link': ['fn.compute']}}]}, {'///': ' A computation. ', 'struct.Computation': {'firstOperand': ['union.Value'], 'secondOperand': ['union.Value'], 'operation': ['union.Operation'], 'timestamp': ['integer'], 'successful': ['boolean']}}, {'///': ' A mathematical variable represented by a `name` that holds a certain `value`. ', 'struct.Variable': {'name': ['string'], 'value': ['number']}}, {'///': ' A basic mathematical operation. ', 'union.Operation': [{'Add': {}}, {'Sub': {}}, {'Mul': {}}, {'Div': {}}]}, {'///': ' A value for computation that can take either a constant or variable form. ', 'union.Value': [{'Constant': {'value': ['number']}}, {'Variable': {'name': ['string']}}]}]

        # Compare the fetched schema with the reference schema
        print(f"Fetched schema: {schema_json}")
        assert schema_json == reference_json, "Fetched schema does not match the reference schema"


    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        assert False, "Demo server is not running or not reachable"
    finally:
        p.kill()
        stdout, stderr = p.communicate(timeout=1)
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")


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
