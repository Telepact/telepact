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
    from ..types.TType import TType


def get_or_parse_type(path: list[object], type_name: str, ctx: 'ParseContext') -> 'TType':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ..types.TObject import TObject
    from ..types.TArray import TArray
    from ..types.TBoolean import TBoolean
    from ..types.TInteger import TInteger
    from ..types.TNumber import TNumber
    from ..types.TObject import TObject
    from ..types.TString import TString
    from ..types.TBytes import TBytes
    from ..types.TMockCall import TMockCall
    from ..types.TMockStub import TMockStub
    from ..types.TSelect import TSelect
    from ..types.TUnion import TUnion
    from ..types.TAny import TAny
    from ...internal.schema.ParseFunctionType import parse_function_result_type
    from ...internal.schema.ParseFunctionType import parse_function_errors_regex
    from ...internal.schema.ParseStructType import parse_struct_type
    from ...internal.schema.ParseUnionType import parse_union_type

    if type_name in ctx.failed_types:
        raise TelepactSchemaParseError(
            [], ctx.telepact_schema_document_names_to_json)

    existing_type = ctx.parsed_types.get(type_name)
    if existing_type is not None:
        return existing_type

    regex_string = r"^(boolean|integer|number|string|any|bytes)|((fn|(union|struct|_ext))\.([a-zA-Z_]\w*))$"
    regex = re.compile(regex_string)

    matcher = regex.match(type_name)
    if not matcher:
        print(f"Type name '{type_name}' does not match expected regex: {regex_string}")
        raise TelepactSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "StringRegexMatchFailed", {
                                "regex": regex_string})],
            ctx.telepact_schema_document_names_to_json)

    standard_type_name = matcher.group(1)
    if standard_type_name is not None:
        return {
            "boolean": TBoolean(),
            "integer": TInteger(),
            "number": TNumber(),
            "string": TString(),
            "bytes": TBytes()
        }.get(standard_type_name, TAny())

    custom_type_name = matcher.group(2)
    this_index = ctx.schema_keys_to_index.get(custom_type_name)
    this_document_name = cast(
        str, ctx.schema_keys_to_document_name.get(custom_type_name))
    if this_index is None:
        raise TelepactSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "TypeUnknown", {
                                "name": custom_type_name})],
            ctx.telepact_schema_document_names_to_json)

    telepact_schema_pseudo_json = cast(
        list[object], ctx.telepact_schema_document_names_to_pseudo_json.get(this_document_name))
    definition = cast(
        dict[str, object], telepact_schema_pseudo_json[this_index])

    type: 'TType'
    try:
        this_path: list[object] = [this_index]
        if custom_type_name.startswith("struct"):
            type = parse_struct_type(this_path, definition, custom_type_name, [],
                                     ctx.copy(document_name=this_document_name))
            ctx.parsed_types[custom_type_name] = type
        elif custom_type_name.startswith("union"):
            type = parse_union_type(this_path, definition, custom_type_name, [], [],
                                    ctx.copy(document_name=this_document_name))
            
            ctx.parsed_types[custom_type_name] = type
        elif custom_type_name.startswith("fn"):
            arg_type = parse_struct_type(path, definition,
                                        custom_type_name, ["->", "_errors"],
                                        ctx.copy(document_name=this_document_name))
            type = TUnion(custom_type_name, {custom_type_name: arg_type}, {
                            custom_type_name: 0})

            ctx.parsed_types[custom_type_name] = type

            result_type = parse_function_result_type(
                this_path,
                definition,
                custom_type_name,
                ctx.copy(document_name=this_document_name)
            )

            ctx.parsed_types[custom_type_name + '.->'] = result_type

            errors_regex = parse_function_errors_regex(
                this_path,
                definition,
                custom_type_name,
                ctx.copy(document_name=this_document_name)
            )

            ctx.fn_error_regexes[custom_type_name] = errors_regex

        else:
            possible_type_extension = {
                '_ext.Select_': TSelect(),
                '_ext.Call_': TMockCall(ctx.parsed_types),
                '_ext.Stub_': TMockStub(ctx.parsed_types),
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
