from typing import TYPE_CHECKING
from uapi.MockUApiSchema import MockUApiSchema


def create_mock_uapi_schema_from_file_json_map(json_documents: dict[str, str]) -> 'MockUApiSchema':
    from uapi.internal.schema.GetMockUApiJson import get_mock_uapi_json
    from uapi.internal.schema.CreateUApiSchemaFromFileJsonMap import create_uapi_schema_from_file_json_map

    final_json_documents = json_documents.copy()
    final_json_documents["mock_"] = get_mock_uapi_json()

    uapi_schema = create_uapi_schema_from_file_json_map(final_json_documents)

    return MockUApiSchema(uapi_schema.original, uapi_schema.parsed, uapi_schema.parsed_request_headers, uapi_schema.parsed_response_headers)
