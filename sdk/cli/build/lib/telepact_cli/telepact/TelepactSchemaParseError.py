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
    from .internal.schema.SchemaParseFailure import SchemaParseFailure


class TelepactSchemaParseError(Exception):
    """
    Indicates failure to parse a telepact Schema.
    """

    def __init__(self, schema_parse_failures: list['SchemaParseFailure'], telepact_schema_document_names_to_json: dict[str, str]):
        from .internal.schema.MapSchemaParseFailuresToPseudoJson import map_schema_parse_failures_to_pseudo_json
        super().__init__(str(map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures, telepact_schema_document_names_to_json)))
        self.schema_parse_failures = schema_parse_failures
        self.schema_parse_failures_pseudo_json = map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures, telepact_schema_document_names_to_json)
