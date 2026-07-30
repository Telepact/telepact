#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
from ...MockTelepactSchema import MockTelepactSchema


def create_mock_telepact_schema_from_file_json_map(json_documents: dict[str, str]) -> 'MockTelepactSchema':
    from .GetMockTelepactJson import get_mock_telepact_json
    from .CreateTelepactSchemaFromFileJsonMap import create_telepact_schema_from_file_json_map
    from .DocumentLocators import copy_document_locators

    final_json_documents = copy_document_locators(json_documents, dict(json_documents))
    final_json_documents["mock_"] = get_mock_telepact_json()

    telepact_schema = create_telepact_schema_from_file_json_map(
        final_json_documents)

    return MockTelepactSchema(telepact_schema.original, telepact_schema.full, telepact_schema.parsed, telepact_schema.parsed_request_headers, telepact_schema.parsed_response_headers)
