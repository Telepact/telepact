import re
from typing import List, Dict, Set, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def get_or_parse_type(path: List[object], type_name: str, this_type_parameter_count: int,
                      u_api_schema_pseudo_json: List[object], schema_keys_to_index: Dict[str, int],
                      parsed_types: Dict[str, 'UType'], type_extensions: Dict[str, 'UType'],
                      all_parse_failures: List[object], failed_types: Set[str]) -> 'UType':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.types.UAny import UAny
    from uapi.internal.types.UArray import UArray
    from uapi.internal.types.UBoolean import UBoolean
    from uapi.internal.types.UGeneric import UGeneric
    from uapi.internal.types.UInteger import UInteger
    from uapi.internal.types.UNumber import UNumber
    from uapi.internal.types.UObject import UObject
    from uapi.internal.types.UString import UString
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
            [{"path": path, "error": "StringRegexMatchFailed", "regex": regex_string}])

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
            [{"path": path, "error": "TypeUnknown", "name": custom_type_name}])
    definition = u_api_schema_pseudo_json[index]

    type_parameter_count_string = matcher.group(6)
    type_parameter_count = int(
        type_parameter_count_string) if type_parameter_count_string else 0

    try:
        if custom_type_name.startswith("struct"):
            type = parse_struct_type([index], definition, custom_type_name, [], type_parameter_count,
                                     u_api_schema_pseudo_json, schema_keys_to_index, parsed_types, type_extensions,
                                     all_parse_failures, failed_types)
        elif custom_type_name.startswith("union"):
            type = parse_union_type([index], definition, custom_type_name, [], [], type_parameter_count,
                                    u_api_schema_pseudo_json, schema_keys_to_index, parsed_types, type_extensions,
                                    all_parse_failures, failed_types)
        elif custom_type_name.startswith("fn"):
            type = parse_function_type([index], definition, custom_type_name, u_api_schema_pseudo_json,
                                       schema_keys_to_index, parsed_types, type_extensions, all_parse_failures,
                                       failed_types)
        else:
            type = type_extensions.get(custom_type_name)
            if type is None:
                raise UApiSchemaParseError(
                    [{"path": [index], "error": "TypeExtensionImplementationMissing", "name": custom_type_name}])

        parsed_types[custom_type_name] = type

        return type
    except UApiSchemaParseError as e:
        all_parse_failures.extend(e.schema_parse_failures)
        failed_types.add(custom_type_name)
        raise UApiSchemaParseError([])
