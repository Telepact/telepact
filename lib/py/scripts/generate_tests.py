from dataclasses import dataclass

cases_filepath = "../../test/cases.txt"
test_filepath = "tests/test_cases.py"

cases_file = open(cases_filepath, "r")
test_file = open(test_filepath, "w")


@dataclass
class Case:
    name: str
    input: str
    output: str


cases = []

current_test_name = None
counter = 0

for l in cases_file:
    line = l.rstrip()

    if line.startswith('"'):
        current_test_name = line[1:-1]
        counter = 1
    elif line == '':
        continue
    elif line.startswith('['):
        lines = line.split('|')
        input = lines[0]
        output = lines[1]

        case = Case('{}_{}'.format(current_test_name, counter), input, output)

        cases.append(case)

        counter += 1

test_file.write('''
import json
import pytest
import asyncio
from typing import Any, Dict, List, Optional
from functools import partial
from lib.py.src.japi.application_error import ApplicationError
from lib.py.src.japi.client_error import ClientError
from lib.py.src.japi.client_options import ClientOptions
from lib.py.src.japi.sync_client import SyncClient
from lib.py.src.japi.processor import Options, Processor


def handle(function_name: str, headers: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
    if function_name == "test":
        error = next((k for k in headers.keys()
                     if k.startswith("error.")), None)
        if "output" in headers:
            try:
                return headers["output"]
            except Exception as e:
                raise RuntimeError(e)
        elif error is not None:
            try:
                error_obj = headers.get(error)
                if not isinstance(error_obj, dict):
                    raise TypeError()
                raise ApplicationError(error, error_obj)
            except TypeError as e:
                raise RuntimeError(e)
        else:
            return {{}}
    else:
        raise RuntimeError()


def assert_output(input_str: str, expected_output_str: str) -> None:
    with open("../../test/example.japi.json") as file:
        json_content = file.read()
    processor = Processor(partial(handle), json_content,
                          Options().set_on_error(lambda e: print(e)))

    expected_output_json = json.loads(expected_output_str)

    # Test JSON
    output = processor.process(input_str.encode("utf-8"))
    output_json = json.loads(output)
    assert expected_output_json == output_json

    # Test binary
    client = SyncClient(lambda m: asyncio.get_event_loop().run_until_complete(
        processor.process(m)), ClientOptions().set_use_binary(True))
    client.call("_ping", {{}}, {{}})  # Warmup
    input_json = json.loads(input_str)

    if expected_output_str.startswith("[\\"error."):
        with pytest.raises(ClientError) as error:
            client.call(input_json[0][9:], input_json[1], input_json[2])
        assert expected_output_json[0] == error.type
        assert expected_output_json[2] == error.body
    else:
        output_java = client.call(
            input_json[0][9:], input_json[1], input_json[2])
        assert expected_output_json[2] == output_java

''')

for case in cases:
    print(case)
    test_file.write('''
def test_{}():
    input = '{}'
    expected_output = '{}'
    assert_output(input, expected_output)

    '''.format(case.name, case.input, case.output))
