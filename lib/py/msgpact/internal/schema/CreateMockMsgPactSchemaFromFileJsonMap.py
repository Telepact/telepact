from typing import TYPE_CHECKING
from ...MockMsgPactSchema import MockMsgPactSchema


def create_mock_vers_api_schema_from_file_json_map(json_documents: dict[str, str]) -> 'MockMsgPactSchema':
    from .GetMockMsgPactJson import get_mock_vers_api_json
    from .CreateMsgPactSchemaFromFileJsonMap import create_vers_api_schema_from_file_json_map

    final_json_documents = json_documents.copy()
    final_json_documents["mock_"] = get_mock_vers_api_json()

    msgpact_schema = create_vers_api_schema_from_file_json_map(
        final_json_documents)

    return MockMsgPactSchema(msgpact_schema.original, msgpact_schema.parsed, msgpact_schema.parsed_request_headers, msgpact_schema.parsed_response_headers)
