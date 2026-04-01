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
from pathlib import Path
from importlib.metadata import version as package_version
import traceback
import asyncio
import pytest
from click.testing import CliRunner
# Adjust the import path according to your project structure
from telepact_cli.cli import main, get_api_from_http
import traceback
import subprocess
import requests
import websockets
import json
import time
from tests.test_data import compare_cases
import os
import shutil
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture(autouse=True, scope='function')
def tmp_dir_manager() -> Generator[None, None, None]:
    tmp_dir = 'tests/tmp'
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    yield

    # Cleanup after tests
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

def test_demo_server_and_fetch_and_mock() -> None:
    p = subprocess.Popen(['uv', 'run', 'telepact', 'demo-server'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd='tests/tmp')
    p_mock: subprocess.Popen | None = None

    try:
        # Check if the server is running
        time.sleep(1)
        response = requests.post('http://localhost:8000/api', data=json.dumps([{}, {'fn.ping_': {}}]))
        assert response.status_code == 200
        assert response.json() == [{}, {'Ok_': {}}]

        # Assert that we can fetch the schema using the cli
        result = subprocess.run(['uv', 'run', 'telepact', 'fetch', '--http-url', 'http://localhost:8000/api', '--output-dir', 'api'], capture_output=True, text=True, cwd='tests/tmp')

        assert result.returncode == 0, f"Schema command failed with output: {result.stdout} and error: {result.stderr}"

        schema_file_path = 'tests/tmp/api/api.telepact.json'
        with open(schema_file_path, 'r') as schema_file:
            schema_content = schema_file.read()
            schema_json = json.loads(schema_content)

        reference_json = [{'///': ' A calculator app that provides basic math computation capabilities. ', 'info.Calculator': {}}, {'///': ' A function that adds two numbers. ', 'fn.add': {'x': 'number', 'y': 'number'}, '->': [{'Ok_': {'result': 'number'}}]}, {'///': ' Compute the `result` of the given `x` and `y` values. ', 'fn.compute': {'x': 'union.Value', 'y': 'union.Value', 'op': 'union.Operation'}, '->': [{'Ok_': {'result': 'number'}}, {'ErrorCannotDivideByZero': {}}]}, {'///': ' Export all saved variables, up to an optional `limit`. ', 'fn.exportVariables': {'limit!': 'integer'}, '->': [{'Ok_': {'variables': ['struct.Variable']}}]}, {'///': ' A function template. ', 'fn.getPaperTape': {}, '->': [{'Ok_': {'tape': ['struct.Computation']}}]}, {'///': ' Save a set of variables as a dynamic map of variable names to their value. ', 'fn.saveVariables': {'variables': {'string': 'number'}}, '->': [{'Ok_': {}}]}, {'fn.showExample': {}, '->': [{'Ok_': {'link': 'fn.compute'}}]}, {'///': ' A computation. ', 'struct.Computation': {'firstOperand': 'union.Value', 'secondOperand': 'union.Value', 'operation': 'union.Operation', 'timestamp': 'integer', 'successful': 'boolean'}}, {'///': ' A mathematical variable represented by a `name` that holds a certain `value`. ', 'struct.Variable': {'name': 'string', 'value': 'number'}}, {'///': ' A basic mathematical operation. ', 'union.Operation': [{'Add': {}}, {'Sub': {}}, {'Mul': {}}, {'Div': {}}]}, {'///': ' A value for computation that can take either a constant or variable form. ', 'union.Value': [{'Constant': {'value': 'number'}}, {'Variable': {'name': 'string'}}]}]

        # Compare the fetched schema with the reference schema
        print(f"Fetched schema: {schema_json}")
        assert schema_json == reference_json, "Fetched schema does not match the reference schema"

        # Assert that we can start the mock server using the fetched schema
        p_mock = subprocess.Popen(['uv', 'run', 'telepact', 'mock', '--http-url', 'http://localhost:8000/api', '--port', '8001'])
        time.sleep(1)

        response_mock = requests.post('http://localhost:8001/api', data=json.dumps([{}, {'fn.add': {'x': 5, 'y': 3}}]))

        assert response_mock.status_code == 200
        assert response_mock.json() == [{}, {'Ok_': {'result': 0.001007557381413671}}] # result is mocked

        async def websocket_request() -> list[dict[str, object]]:
            async with websockets.connect('ws://localhost:8001/api') as websocket:
                await websocket.send(json.dumps([{}, {'fn.add': {'x': 2, 'y': 4}}]))
                response_text = await websocket.recv()
                return json.loads(response_text)

        ws_response = asyncio.run(websocket_request())
        expected_ws_response = [{}, {'Ok_': {'result': 0.0014801179065742148}}]
        assert ws_response == expected_ws_response


    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        assert False, "Demo server is not running or not reachable"
    finally:
        p.terminate()
        try:
            stdout, stderr = p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
            stdout, stderr = p.communicate(timeout=5)
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")

        if p_mock:
            p_mock.terminate()
            try:
                stdout_mock, stderr_mock = p_mock.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                p_mock.kill()
                stdout_mock, stderr_mock = p_mock.communicate(timeout=5)
            print(f"Mock server stdout: {stdout_mock}")
            print(f"Mock server stderr: {stderr_mock}")


def test_fetch_sets_content_type_header() -> None:
    expected_request = b'[{"@time_": 5000}, {"fn.api_": {}}]'
    ok_response = b'[{},{"Ok_":{"api":[]}}]'
    requests_seen: list[tuple[str | None, bytes]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            requests_seen.append((self.headers.get('Content-Type'), body))
            if self.headers.get('Content-Type') != 'application/json':
                payload = b'[{},{"ErrorParseFailure_":{"reasons":[{"ExpectedJsonArrayOfTwoObjects":{}}]}}]'
            elif body != expected_request:
                payload = b'[{},{"ErrorUnknown_":{}}]'
            else:
                payload = ok_response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        api_json = get_api_from_http(f'http://127.0.0.1:{server.server_port}/api')
        assert json.loads(api_json) == []
        assert requests_seen == [('application/json', expected_request)]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_version_flag(runner: CliRunner) -> None:
    expected_version = package_version('telepact-cli')

    result = runner.invoke(main, ['--version'])

    assert result.exit_code == 0
    assert result.output.strip() == f'telepact, version {expected_version}'


@pytest.mark.parametrize("assertion, old, new, expected, expected_code", compare_cases)
def test_compare(runner: CliRunner, assertion: str, old: dict, new: dict, expected: list[str], expected_code: int) -> None:
    import os
    os.makedirs('tests/tmp/compare/old', exist_ok=True)
    os.makedirs('tests/tmp/compare/new', exist_ok=True)
    with open('tests/tmp/compare/old/schema.telepact.json', 'w') as f:
        old_json = json.dumps(old, indent=2)
        f.write(old_json)
    with open('tests/tmp/compare/new/schema.telepact.json', 'w') as f:
        new_json = json.dumps(new, indent=2)
        f.write(new_json)

    result = runner.invoke(
        main, ['compare', '--old-schema-dir', 'tests/tmp/compare/old', '--new-schema-dir', 'tests/tmp/compare/new'])

    # print stack trace
    import traceback

    # Assuming result.exc_info is a tuple (exc_type, exc_value, exc_traceback)
    if result.exc_info:
        # Format the traceback and print it
        traceback_str = ''.join(traceback.format_exception(*result.exc_info))
        print(traceback_str)

    print(f'Output: {result.output}')

    assert expected_code == result.exit_code
    output_lines = [line.strip() for line in result.output.split('\n') if line.strip()]
    assert expected == output_lines


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

    generated = Path('tests/output/java/test.java').read_text()
    generated_nested = Path('tests/output/java/selectNested.java').read_text()
    assert 'if (!resultUnion.containsKey("Ok_"))' not in generated
    assert 'final var theseFields = (List<Object>) resultUnion.getOrDefault("Ok_", new ArrayList<>());' in generated
    assert 'final var theseFields = (List<Object>) this.pseudoJson.getOrDefault("struct.ResultCard", new ArrayList<>());' in generated_nested
    assert 'final var theseTags = (Map<String, Object>) this.pseudoJson.getOrDefault("union.ResultItem", new HashMap<>());' in generated_nested
    assert 'final var theseFields = (List<Object>) theseTags.getOrDefault("Card", new ArrayList<>());' in generated_nested


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

    generated = Path('tests/output/py/gen_types.py').read_text()
    assert "if 'Ok_' not in result_union:" not in generated
    assert 'these_fields = cast(list[object], result_union.get("Ok_", []))' in generated
    assert 'these_fields = cast(list[object], self.pseudo_json.get("struct.ResultCard", []))' in generated
    assert 'these_fields = cast(list[object], these_tags.get("Card", []))' in generated


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

    generated = Path('tests/output/ts/genTypes.ts').read_text()
    assert '}static ' not in generated
    assert '}ok' not in generated
    assert "const theseFields = resultUnion[\"Ok_\"] ?? [];" in generated
    assert "if (!theseFields.includes('field1')) {" in generated
    assert "const theseFields = this.pseudoJson[\"struct.ResultCard\"] ?? [];" in generated
    assert "const theseTags = this.pseudoJson[\"union.ResultItem\"] ?? {};" in generated
    assert "const theseFields = theseTags[\"Card\"] ?? [];" in generated


def test_codegen_help_mentions_package_requirement_for_go_and_java(runner: CliRunner) -> None:
    result = runner.invoke(main, ['codegen', '--help'])

    assert result.exit_code == 0
    assert 'Package name (required when --lang is "java" or "go")' in result.output



def test_command_go_requires_package(runner: CliRunner) -> None:
    result = runner.invoke(
        main, ['codegen', '--schema-dir', 'tests/data', '--lang', 'go', '--out', 'tests/output/go'])

    assert result.exit_code != 0
    assert '--package is required when --lang is go' in result.output



def test_command_go(runner: CliRunner) -> None:
    output_dir = Path('tests/output/go')
    result = runner.invoke(
        main, ['codegen', '--schema-dir', 'tests/data', '--lang', 'go', '--out', str(output_dir), '--package', 'output'])

    if result.exc_info:
        traceback_str = ''.join(traceback.format_exception(*result.exc_info))
        print(traceback_str)

    print(f'Output: {result.output}')

    assert result.exit_code == 0

    # open the generated file and check if it contains the expected content
    # TODO: implement this part

def test_empty_schema(runner: CliRunner) -> None:
    os.makedirs('tests/tmp/wrong', exist_ok=True)

    # Copy the file in tests/data to tests/tmp/wrong/api.wrong.json
    shutil.copy('tests/data/example1.telepact.json', 'tests/tmp/wrong/api.wrong.json')

    result = runner.invoke(
        main, ['codegen', '--schema-dir', 'tests/tmp/wrong', '--lang', 'py', '--out', 'tests/output/empty'])

    # print stack trace
    import traceback

    # Assuming result.exc_info is a tuple (exc_type, exc_value, exc_traceback)
    if result.exc_info:
        # Format the traceback and print it
        traceback_str = ''.join(traceback.format_exception(*result.exc_info))
        print(traceback_str)

    print(f'Output: {result.output}')

    assert result.exit_code != 0
    assert "FileNamePatternInvalid" in traceback_str
