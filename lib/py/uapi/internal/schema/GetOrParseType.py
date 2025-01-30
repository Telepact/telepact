import re
from typing import TYPE_CHECKING, cast
from uapi.UApiSchemaParseError import UApiSchemaParseError
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from uapi.internal.schema.ParseContext import ParseContext
    from uapi.internal.types.UType import UType


def get_or_parse_type(path: list[object], type_name: str, ctx: 'ParseContext') -> 'UType':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.types.UObject import UObject
    from uapi.internal.types.UArray import UArray
    from uapi.internal.types.UBoolean import UBoolean
    from uapi.internal.types.UInteger import UInteger
    from uapi.internal.types.UNumber import UNumber
    from uapi.internal.types.UObject import UObject
    from uapi.internal.types.UString import UString
    from uapi.internal.types.UMockCall import UMockCall
    from uapi.internal.types.UMockStub import UMockStub
    from uapi.internal.types.USelect import USelect
    from uapi.internal.types.UAny import UAny
    from uapi.internal.schema.ParseFunctionType import parse_function_type
    from uapi.internal.schema.ParseStructType import parse_struct_type
    from uapi.internal.schema.ParseUnionType import parse_union_type

    if type_name in ctx.failed_types:
        raise UApiSchemaParseError([], ctx.uapi_schema_document_names_to_json)

    existing_type = ctx.parsed_types.get(type_name)
    if existing_type is not None:
        return existing_type

    regex_string = r"^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\.([a-zA-Z_]\w*))$"
    regex = re.compile(regex_string)

    matcher = regex.match(type_name)
    if not matcher:
        raise UApiSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "StringRegexMatchFailed", {
                                "regex": regex_string})],
            ctx.uapi_schema_document_names_to_json)

    standard_type_name = matcher.group(1)
    if standard_type_name is not None:
        return {
            "boolean": UBoolean(),
            "integer": UInteger(),
            "number": UNumber(),
            "string": UString(),
            "array": UArray(),
            "object": UObject()
        }.get(standard_type_name, UAny())

    custom_type_name = matcher.group(2)
    this_index = ctx.schema_keys_to_index.get(custom_type_name)
    this_document_name = cast(
        str, ctx.schema_keys_to_document_name.get(custom_type_name))
    if this_index is None:
        raise UApiSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "TypeUnknown", {
                                "name": custom_type_name})],
            ctx.uapi_schema_document_names_to_json)

    u_api_schema_pseudo_json = cast(
        list[object], ctx.uapi_schema_document_names_to_pseudo_json.get(this_document_name))
    definition = cast(
        dict[str, object], u_api_schema_pseudo_json[this_index])

    type: 'UType'
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
                '_ext.Select_': USelect(),
                '_ext.Call_': UMockCall(ctx.parsed_types),
                '_ext.Stub_': UMockStub(ctx.parsed_types),
            }.get(custom_type_name)

            if not possible_type_extension:
                raise UApiSchemaParseError([
                    SchemaParseFailure(
                        ctx.document_name,
                        [this_index],
                        'TypeExtensionImplementationMissing',
                        {'name': custom_type_name}
                    ),
                ], ctx.uapi_schema_document_names_to_json)

            type = possible_type_extension

        ctx.parsed_types[custom_type_name] = type

        return type
    except UApiSchemaParseError as e:
        ctx.all_parse_failures.extend(e.schema_parse_failures)
        ctx.failed_types.add(custom_type_name)
        raise UApiSchemaParseError([], ctx.uapi_schema_document_names_to_json)
