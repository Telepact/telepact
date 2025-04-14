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
from ...internal.schema.DerivePossibleSelects import derive_possible_select
from ...internal.schema.GetOrParseType import get_or_parse_type
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ..types.TSelect import TSelect

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ..types.TType import TType
    from ..types.TUnion import TUnion


def parse_function_result_type(path: list[object], function_definition_as_parsed_json: dict[str, object],
                        schema_key: str,
                        ctx: 'ParseContext') -> 'TUnion':
    from ...internal.schema.ParseStructType import parse_struct_type
    from ...internal.schema.ParseUnionType import parse_union_type
    from ...internal.schema.ParseUnionType import parse_union_type
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    from ..types.TUnion import TUnion

    parse_failures = []

    result_schema_key = "->"

    result_type = None
    if result_schema_key not in function_definition_as_parsed_json:
        parse_failures.append(SchemaParseFailure(
            ctx.document_name, path, "RequiredObjectKeyMissing", {'key': result_schema_key}))
    else:
        try:
            result_type = parse_union_type(path, function_definition_as_parsed_json,
                                           result_schema_key, list(
                                               function_definition_as_parsed_json.keys()),
                                           ["Ok_"], ctx)
        except TelepactSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)


    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    fn_select_type = derive_possible_select(
        schema_key, cast(TUnion, result_type))
    select_type = cast(TSelect, get_or_parse_type([], '_ext.Select_', ctx))
    select_type.possible_selects[schema_key] = fn_select_type

    return cast(TUnion, result_type)

def parse_function_errors_regex(path: list[object], function_definition_as_parsed_json: dict[str, object],
                        schema_key: str,
                        ctx: 'ParseContext') -> str:
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ...TelepactSchemaParseError import TelepactSchemaParseError

    parse_failures = []

    errors_regex_key = "_errors"

    regex_path = path + [errors_regex_key]

    errors_regex: str | None = None
    if errors_regex_key in function_definition_as_parsed_json and not schema_key.endswith("_"):
        parse_failures.append(SchemaParseFailure(
            ctx.document_name, regex_path, "ObjectKeyDisallowed", {}))
    else:
        errors_regex_init = function_definition_as_parsed_json.get(
            errors_regex_key, "^errors\\..*$")

        if not isinstance(errors_regex_init, str):
            this_parse_failures = get_type_unexpected_parse_failure(
                ctx.document_name, regex_path, errors_regex_init, "String")
            parse_failures.extend(this_parse_failures)
        else:
            errors_regex = errors_regex_init

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    return cast(str, errors_regex)