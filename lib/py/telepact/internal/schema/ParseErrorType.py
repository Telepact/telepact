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

from typing import TYPE_CHECKING, cast
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ..types.TError import TError

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext


def parse_error_type(path: list[object], error_definition_as_parsed_json: dict[str, object],
                     schema_key: str,
                     ctx: 'ParseContext') -> 'TError':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.ParseUnionType import parse_union_type

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                ctx.document_name, cast(list[object], loop_path), "ObjectKeyDisallowed", {}))

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    error = parse_union_type(path, error_definition_as_parsed_json, schema_key, [], [],
                             ctx)

    return TError(schema_key, error)
