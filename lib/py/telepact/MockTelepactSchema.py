from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .internal.types.VFieldDeclaration import VFieldDeclaration
    from .internal.types.VType import VType


class MockTelepactSchema:
    """
    A parsed telepact schema.
    """

    def __init__(self, original: list[object], parsed: dict[str, 'VType'], parsed_request_headers: dict[str, 'VFieldDeclaration'],
                 parsed_response_headers: dict[str, 'VFieldDeclaration']):
        self.original = original
        self.parsed = parsed
        self.parsed_request_headers = parsed_request_headers
        self.parsed_response_headers = parsed_response_headers

    @staticmethod
    def from_json(json: str) -> 'MockTelepactSchema':
        from .internal.schema.CreateMockTelepactSchemaFromFileJsonMap import create_mock_vers_api_schema_from_file_json_map
        return create_mock_vers_api_schema_from_file_json_map({"auto_": json})

    @staticmethod
    def from_file_json_map(file_json_map: dict[str, str]) -> 'MockTelepactSchema':
        from .internal.schema.CreateMockTelepactSchemaFromFileJsonMap import create_mock_vers_api_schema_from_file_json_map
        return create_mock_vers_api_schema_from_file_json_map(file_json_map)

    @staticmethod
    def from_directory(directory: str) -> 'MockTelepactSchema':
        from .internal.schema.CreateMockTelepactSchemaFromFileJsonMap import create_mock_vers_api_schema_from_file_json_map
        from .internal.schema.GetSchemaFileMap import get_schema_file_map
        schema_file_map = get_schema_file_map(directory)
        return create_mock_vers_api_schema_from_file_json_map(schema_file_map)
