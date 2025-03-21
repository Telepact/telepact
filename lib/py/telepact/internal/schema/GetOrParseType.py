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

import re
from typing import TYPE_CHECKING, cast
from ...TelepactSchemaParseError import TelepactSchemaParseError
from ...internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ..types.VType import VType


def get_or_parse_type(path: list[object], type_name: str, ctx: 'ParseContext') -> 'VType':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ..types.VObject import VObject
    from ..types.VArray import VArray
    from ..types.VBoolean import VBoolean
    from ..types.VInteger import VInteger
    from ..types.VNumber import VNumber
    from ..types.VObject import VObject
    from ..types.VString import VString
    from ..types.VMockCall import VMockCall
    from ..types.VMockStub import VMockStub
    from ..types.VSelect import VSelect
    from ..types.VAny import VAny
    from ...internal.schema.ParseFunctionType import parse_function_type
    from ...internal.schema.ParseStructType import parse_struct_type
    from ...internal.schema.ParseUnionType import parse_union_type

    if type_name in ctx.failed_types:
        raise TelepactSchemaParseError(
            [], ctx.telepact_schema_document_names_to_json)

    existing_type = ctx.parsed_types.get(type_name)
    if existing_type is not None:
        return existing_type

    regex_string = r"^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\.([a-zA-Z_]\w*))$"
    regex = re.compile(regex_string)

    matcher = regex.match(type_name)
    if not matcher:
        raise TelepactSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "StringRegexMatchFailed", {
                                "regex": regex_string})],
            ctx.telepact_schema_document_names_to_json)

    standard_type_name = matcher.group(1)
    if standard_type_name is not None:
        return {
            "boolean": VBoolean(),
            "integer": VInteger(),
            "number": VNumber(),
            "string": VString(),
            "array": VArray(),
            "object": VObject()
        }.get(standard_type_name, VAny())

    custom_type_name = matcher.group(2)
    this_index = ctx.schema_keys_to_index.get(custom_type_name)
    this_document_name = cast(
        str, ctx.schema_keys_to_document_name.get(custom_type_name))
    if this_index is None:
        raise TelepactSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "TypeUnknown", {
                                "name": custom_type_name})],
            ctx.telepact_schema_document_names_to_json)

    u_api_schema_pseudo_json = cast(
        list[object], ctx.telepact_schema_document_names_to_pseudo_json.get(this_document_name))
    definition = cast(
        dict[str, object], u_api_schema_pseudo_json[this_index])

    type: 'VType'
    try:
        this_path: list[object] = [this_index]
        if custom_type_name.startswith("struct"):
            type = parse_struct_type(this_path, definition, custom_type_name, [],
                                     ctx.copy(document_name=this_document_name))
        elif custom_type_name.startswith("union"):
            type = parse_union_type(this_path, definition, custom_type_name, [], [],
                                    ctx.copy(document_name=this_document_name))
        elif custom_type_name.startswith("fn"):
            type = parse_function_type(this_path, definition, custom_type_name,
                                       ctx.copy(document_name=this_document_name))
        else:
            possible_type_extension = {
                '_ext.Select_': VSelect(),
                '_ext.Call_': VMockCall(ctx.parsed_types),
                '_ext.Stub_': VMockStub(ctx.parsed_types),
            }.get(custom_type_name)

            if not possible_type_extension:
                raise TelepactSchemaParseError([
                    SchemaParseFailure(
                        ctx.document_name,
                        [this_index],
                        'TypeExtensionImplementationMissing',
                        {'name': custom_type_name}
                    ),
                ], ctx.telepact_schema_document_names_to_json)

            type = possible_type_extension

        ctx.parsed_types[custom_type_name] = type

        return type
    except TelepactSchemaParseError as e:
        ctx.all_parse_failures.extend(e.schema_parse_failures)
        ctx.failed_types.add(custom_type_name)
        raise TelepactSchemaParseError(
            [], ctx.telepact_schema_document_names_to_json)
