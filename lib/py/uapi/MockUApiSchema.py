from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UType import UType


class MockUApiSchema:
    """
    A parsed uAPI schema.
    """

    def __init__(self, original: list[object], parsed: dict[str, 'UType'], parsed_request_headers: dict[str, 'UFieldDeclaration'],
                 parsed_response_headers: dict[str, 'UFieldDeclaration']):
        self.original = original
        self.parsed = parsed
        self.parsed_request_headers = parsed_request_headers
        self.parsed_response_headers = parsed_response_headers

    @staticmethod
    def from_json(json: str) -> 'MockUApiSchema':
        from uapi.internal.schema.CreateMockUApiSchemaFromFileJsonMap import create_mock_uapi_schema_from_file_json_map
        return create_mock_uapi_schema_from_file_json_map({"auto_": json})

    @staticmethod
    def from_file_json_map(file_json_map: dict[str, str]) -> 'MockUApiSchema':
        from uapi.internal.schema.CreateMockUApiSchemaFromFileJsonMap import create_mock_uapi_schema_from_file_json_map
        return create_mock_uapi_schema_from_file_json_map(file_json_map)

    @staticmethod
    def from_directory(directory: str) -> 'MockUApiSchema':
        from uapi.internal.schema.CreateMockUApiSchemaFromFileJsonMap import create_mock_uapi_schema_from_file_json_map
        from uapi.internal.schema.GetSchemaFileMap import get_schema_file_map
        schema_file_map = get_schema_file_map(directory)
        return create_mock_uapi_schema_from_file_json_map(schema_file_map)
