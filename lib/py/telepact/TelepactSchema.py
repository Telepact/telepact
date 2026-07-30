#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .internal.types.TFieldDeclaration import TFieldDeclaration
    from .internal.types.TType import TType


class TelepactSchema:
    """
    A parsed telepact schema.
    """

    def __init__(self, original: list[object], full: list[object], parsed: dict[str, 'TType'], parsed_request_headers: dict[str, 'TFieldDeclaration'],
                 parsed_response_headers: dict[str, 'TFieldDeclaration']):
        self.original = original
        self.full = full
        self.parsed = parsed
        self.parsed_request_headers = parsed_request_headers
        self.parsed_response_headers = parsed_response_headers

    @staticmethod
    def from_json(json: str) -> 'TelepactSchema':
        from .internal.schema.CreateTelepactSchemaFromFileJsonMap import create_telepact_schema_from_file_json_map
        return create_telepact_schema_from_file_json_map({"auto_": json})

    @staticmethod
    def from_file_json_map(file_json_map: dict[str, str]) -> 'TelepactSchema':
        from .internal.schema.CreateTelepactSchemaFromFileJsonMap import create_telepact_schema_from_file_json_map
        return create_telepact_schema_from_file_json_map(file_json_map)

    @staticmethod
    def from_directory(directory: str) -> 'TelepactSchema':
        from .internal.schema.CreateTelepactSchemaFromFileJsonMap import create_telepact_schema_from_file_json_map
        from .internal.schema.GetSchemaFileMap import get_schema_file_map
        schema_file_map = get_schema_file_map(directory)
        return create_telepact_schema_from_file_json_map(schema_file_map)
