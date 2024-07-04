import re
from typing import TYPE_CHECKING, cast
from uapi.UApiSchemaParseError import UApiSchemaParseError
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def get_or_parse_type(path: list[object], type_name: str, this_type_parameter_count: int,
                      u_api_schema_pseudo_json: list[object], schema_keys_to_index: dict[str, int],
                      parsed_types: dict[str, 'UType'], all_parse_failures: list['SchemaParseFailure'],
                      failed_types: set[str]) -> 'UType':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.types.UObject import UObject
    from uapi.internal.types.UArray import UArray
    from uapi.internal.types.UBoolean import UBoolean
    from uapi.internal.types.UGeneric import UGeneric
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

    if type_name in failed_types:
        raise UApiSchemaParseError([])

    existing_type = parsed_types.get(type_name)
    if existing_type is not None:
        return existing_type

    if this_type_parameter_count > 0:
        generic_regex = "|(T.([%s]))" % (
            "0-%d" % (this_type_parameter_count - 1) if this_type_parameter_count > 1 else "0")
    else:
        generic_regex = ""

    regex_string = r"^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\.([a-zA-Z_]\w*)%s)$" % generic_regex
    regex = re.compile(regex_string)

    matcher = regex.match(type_name)
    if not matcher:
        raise UApiSchemaParseError(
            [SchemaParseFailure(path, "StringRegexMatchFailed", {"regex": regex_string}, None)])

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

    if this_type_parameter_count > 0:
        generic_parameter_index_string = matcher.group(9)
        if generic_parameter_index_string is not None:
            generic_parameter_index = int(generic_parameter_index_string)
            return UGeneric(generic_parameter_index)

    custom_type_name = matcher.group(2)
    index = schema_keys_to_index.get(custom_type_name)
    if index is None:
        raise UApiSchemaParseError(
            [SchemaParseFailure(path, "TypeUnknown", {"name": custom_type_name}, None)])
    definition = cast(dict[str, object], u_api_schema_pseudo_json[index])

    type_parameter_count_string = matcher.group(6)
    type_parameter_count = int(
        type_parameter_count_string) if type_parameter_count_string else 0

    type: 'UType'
    try:
        if custom_type_name.startswith("struct"):
            type = parse_struct_type([index], definition, custom_type_name, [], type_parameter_count,
                                     u_api_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                     all_parse_failures, failed_types)
        elif custom_type_name.startswith("union"):
            type = parse_union_type([index], definition, custom_type_name, [], [], type_parameter_count,
                                    u_api_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                    all_parse_failures, failed_types)
        elif custom_type_name.startswith("fn"):
            type = parse_function_type([index], definition, custom_type_name, u_api_schema_pseudo_json,
                                       schema_keys_to_index, parsed_types, all_parse_failures,
                                       failed_types)
        else:
            possible_type_extension = {
                '_ext.Select_': USelect(parsed_types),
                '_ext.Call_': UMockCall(parsed_types),
                '_ext.Stub_': UMockStub(parsed_types),
            }.get(custom_type_name)

            if not possible_type_extension:
                raise UApiSchemaParseError([
                    SchemaParseFailure(
                        [index],
                        'TypeExtensionImplementationMissing',
                        {'name': custom_type_name},
                        None,
                    ),
                ])

            type = possible_type_extension

        parsed_types[custom_type_name] = type

        return type
    except UApiSchemaParseError as e:
        all_parse_failures.extend(e.schema_parse_failures)
        failed_types.add(custom_type_name)
        raise UApiSchemaParseError([])
