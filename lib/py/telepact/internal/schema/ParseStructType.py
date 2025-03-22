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
from ..types.TStruct import TStruct

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ..types.TType import TType


def parse_struct_type(path: list[object], struct_definition_as_pseudo_json: dict[str, object],
                      schema_key: str, ignore_keys: list[str],
                      ctx: 'ParseContext') -> 'TStruct':
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ...internal.schema.ParseStructFields import parse_struct_fields
    from ...TelepactSchemaParseError import TelepactSchemaParseError

    parse_failures = []
    other_keys = set(struct_definition_as_pseudo_json.keys())

    other_keys.discard(schema_key)
    other_keys.discard("///")
    other_keys.discard("_ignoreIfDuplicate")
    for ignore_key in ignore_keys:
        other_keys.discard(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                ctx.document_name, loop_path, "ObjectKeyDisallowed", {}))

    this_path = path + [schema_key]
    def_init = cast(dict[str, object],
                    struct_definition_as_pseudo_json.get(schema_key))

    definition = None
    if not isinstance(def_init, dict):
        branch_parse_failures = get_type_unexpected_parse_failure(
            ctx.document_name, this_path, def_init, "Object")
        parse_failures.extend(branch_parse_failures)
    else:
        definition = def_init

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    fields = parse_struct_fields(this_path, definition, False, ctx)

    return TStruct(schema_key, fields)
