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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .internal.types.TFieldDeclaration import TFieldDeclaration
    from .internal.types.TType import TType


class TelepactSchema:
    """
    A parsed telepact schema.
    """

    def __init__(self, original: list[object], parsed: dict[str, 'TType'], parsed_request_headers: dict[str, 'TFieldDeclaration'],
                 parsed_response_headers: dict[str, 'TFieldDeclaration']):
        self.original = original
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
