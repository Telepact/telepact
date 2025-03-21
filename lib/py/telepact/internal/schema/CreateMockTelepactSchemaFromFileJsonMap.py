from typing import TYPE_CHECKING
from ...MockTelepactSchema import MockTelepactSchema


def create_mock_vers_api_schema_from_file_json_map(json_documents: dict[str, str]) -> 'MockTelepactSchema':
    from .GetMockTelepactJson import get_mock_vers_api_json
    from .CreateTelepactSchemaFromFileJsonMap import create_vers_api_schema_from_file_json_map

    final_json_documents = json_documents.copy()
    final_json_documents["mock_"] = get_mock_vers_api_json()

    telepact_schema = create_vers_api_schema_from_file_json_map(
        final_json_documents)

    return MockTelepactSchema(telepact_schema.original, telepact_schema.parsed, telepact_schema.parsed_request_headers, telepact_schema.parsed_response_headers)
