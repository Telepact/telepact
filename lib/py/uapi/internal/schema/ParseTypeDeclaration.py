import re
from typing import TYPE_CHECKING
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def parse_type_declaration(path: list[object], type_declaration_array: list[object],
                           this_type_parameter_count: int, uapi_schema_pseudo_json: list[object],
                           schema_keys_to_index: dict[str, int], parsed_types: dict[str, 'UType'],
                           type_extensions: dict[str, 'UType'], all_parse_failures: list['SchemaParseFailure'],
                           failed_types: set[str]) -> 'UTypeDeclaration':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetOrParseType import get_or_parse_type
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.types.UGeneric import UGeneric

    if not type_declaration_array:
        raise UApiSchemaParseError(
            [SchemaParseFailure(path, "EmptyArrayDisallowed", {}, None)])

    base_path = path + [0]
    base_type = type_declaration_array[0]

    if not isinstance(base_type, str):
        this_parse_failures = get_type_unexpected_parse_failure(
            base_path, base_type, "String")
        raise UApiSchemaParseError(this_parse_failures)

    root_type_string = base_type

    regex_string = r"^(.+?)(\?)?$"
    regex = re.compile(regex_string)

    matcher = regex.match(root_type_string)
    if not matcher:
        raise UApiSchemaParseError([SchemaParseFailure(
            base_path, "StringRegexMatchFailed", {"regex": regex_string}, None)])

    type_name = matcher.group(1)
    nullable = bool(matcher.group(2))

    type_ = get_or_parse_type(base_path, type_name, this_type_parameter_count, uapi_schema_pseudo_json,
                              schema_keys_to_index, parsed_types, type_extensions, all_parse_failures, failed_types)

    if isinstance(type_, UGeneric) and nullable:
        raise UApiSchemaParseError([SchemaParseFailure(
            base_path, "StringRegexMatchFailed", {"regex": r"^(.+?)[^\?]$"}, None)])

    given_type_parameter_count = len(type_declaration_array) - 1
    if type_.get_type_parameter_count() != given_type_parameter_count:
        print('path', path)
        print('type_.get_type_parameter_count()',
              type_.get_type_parameter_count())
        print('given_type_parameter_count', given_type_parameter_count)
        raise UApiSchemaParseError([SchemaParseFailure(path, "ArrayLengthUnexpected",
                                                       {"actual": len(type_declaration_array),
                                                        "expected": type_.get_type_parameter_count() + 1}, None)])

    parse_failures = []
    type_parameters = []
    given_type_parameters = type_declaration_array[1:]

    for index, e in enumerate(given_type_parameters, start=1):
        loop_path = path + [index]

        if not isinstance(e, list):
            this_parse_failures = get_type_unexpected_parse_failure(
                loop_path, e, "Array")
            parse_failures.extend(this_parse_failures)
            continue

        l = e

        try:
            type_parameter_type_declaration = parse_type_declaration(loop_path, l, this_type_parameter_count,
                                                                     uapi_schema_pseudo_json, schema_keys_to_index,
                                                                     parsed_types, type_extensions, all_parse_failures,
                                                                     failed_types)

            type_parameters.append(type_parameter_type_declaration)
        except UApiSchemaParseError as e2:
            parse_failures.extend(e2.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    return UTypeDeclaration(type_, nullable, type_parameters)
