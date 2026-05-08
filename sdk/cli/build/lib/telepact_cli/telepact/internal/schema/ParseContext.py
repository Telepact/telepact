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

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    from ..types.TType import TType


class ParseContext:
    document_name: str
    telepact_schema_document_names_to_pseudo_json: dict[str, list[object]]
    telepact_schema_document_names_to_json: dict[str, str]
    schema_keys_to_document_name: dict[str, str]
    schema_keys_to_index: dict[str, int]
    parsed_types: dict[str, 'TType']
    fn_error_regexes: dict[str, str]
    all_parse_failures: list['SchemaParseFailure']
    failed_types: set[str]

    def __init__(self, document_name: str, telepact_schema_document_names_to_pseudo_json: dict[str, list[object]],
                 telepact_schema_document_names_to_json: dict[str, str],
                 schema_keys_to_document_name: dict[str, str], schema_keys_to_index: dict[str, int],
                 parsed_types: dict[str, 'TType'], fn_error_regexes: dict[str, str],
                 all_parse_failures: list['SchemaParseFailure'], failed_types: set[str]) -> None:
        self.document_name = document_name
        self.telepact_schema_document_names_to_pseudo_json = telepact_schema_document_names_to_pseudo_json
        self.telepact_schema_document_names_to_json = telepact_schema_document_names_to_json
        self.schema_keys_to_document_name = schema_keys_to_document_name
        self.schema_keys_to_index = schema_keys_to_index
        self.parsed_types = parsed_types
        self.fn_error_regexes = fn_error_regexes
        self.all_parse_failures = all_parse_failures
        self.failed_types = failed_types

    def copy(self, document_name: Optional[str] = None) -> 'ParseContext':
        return ParseContext(document_name if document_name is not None else self.document_name,
                            self.telepact_schema_document_names_to_pseudo_json, self.telepact_schema_document_names_to_json,
                            self.schema_keys_to_document_name, self.schema_keys_to_index,
                            self.parsed_types, self.fn_error_regexes, self.all_parse_failures, self.failed_types)
