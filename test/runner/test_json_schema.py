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

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).parents[2]
JSON_SCHEMA_PATH = ROOT / "common" / "json-schema.json"

VALID_SCHEMA_PATHS = [
    ROOT / "common" / "auth.telepact.yaml",
    ROOT / "common" / "internal.telepact.yaml",
    ROOT / "common" / "mock-internal.telepact.yaml",
    ROOT / "test" / "runner" / "schema" / "api_examples_mock" / "api_examples_mock.telepact.json",
    ROOT / "test" / "runner" / "schema" / "auth" / "auth.telepact.json",
    ROOT / "test" / "runner" / "schema" / "binary" / "binary.telepact.json",
    ROOT / "test" / "runner" / "schema" / "example" / "example.telepact.json",
    ROOT / "test" / "runner" / "schema" / "load" / "load.telepact.json",
    ROOT / "test" / "runner" / "schema" / "mockgen" / "mockgen.telepact.json",
    ROOT / "test" / "runner" / "schema" / "parse" / "schema.telepact.json",
]

INVALID_SCHEMAS = [
    [{"struct.Example": {"field": "stringly"}}],
    [{"struct.Example": {"field": "thing.Unknown"}}],
    [{"struct.Example.extra": {}}],
    [{"struct.Example": {"InvalidField": "string"}}],
    [{"union.Example": []}],
    [{"union.Example": [{"One": {}, "Two": {}}]}],
    [{"struct.One": {}, "struct.Two": {}}],
    [{"fn.example": {}, "->": [{"Error": {}}]}],
    [{"fn.one": {}, "fn.two": {}, "->": [{"Ok_": {}}]}],
    [{"fn.example": {}, "_errors": "^.*$", "->": [{"Ok_": {}}]}],
    [{"headers.Example": {"@trace!": "string"}, "->": {}}],
    [{"///": "A definition is required."}],
    [{"invalid.Example": {}}],
]


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = json.loads(JSON_SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.mark.parametrize(
    "schema_path",
    VALID_SCHEMA_PATHS,
    ids=lambda path: path.name,
)
def test_json_schema_accepts_telepact_schemas(
    validator: Draft202012Validator,
    schema_path: Path,
) -> None:
    schema_document = yaml.safe_load(schema_path.read_text())
    errors = sorted(
        validator.iter_errors(schema_document),
        key=lambda error: list(error.path),
    )

    assert errors == []


def test_json_schema_accepts_internal_function_controls(
    validator: Draft202012Validator,
) -> None:
    schema_document = [
        {
            "fn.internal_": {},
            "_errors": "^errors\\.Validation_$",
            "->": [{"Error": {}}, {"Ok_": {}}],
        }
    ]

    assert validator.is_valid(schema_document)


@pytest.mark.parametrize("schema_document", INVALID_SCHEMAS)
def test_json_schema_rejects_invalid_telepact_schemas(
    validator: Draft202012Validator,
    schema_document: list[object],
) -> None:
    assert not validator.is_valid(schema_document)
