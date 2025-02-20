import re
from typing import TYPE_CHECKING
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ...internal.types.UTypeDeclaration import UTypeDeclaration

if TYPE_CHECKING:
    from ...internal.types.UType import UType
    from ...internal.schema.ParseContext import ParseContext


def parse_type_declaration(path: list[object], type_declaration_array: list[object],
                           ctx: 'ParseContext') -> 'UTypeDeclaration':
    from ...UApiSchemaParseError import UApiSchemaParseError
    from ...internal.schema.GetOrParseType import get_or_parse_type
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure

    if not type_declaration_array:
        raise UApiSchemaParseError(
            [SchemaParseFailure(ctx.document_name, path, "EmptyArrayDisallowed", {})], ctx.uapi_schema_document_names_to_json)

    base_path = path + [0]
    base_type = type_declaration_array[0]

    if not isinstance(base_type, str):
        this_parse_failures = get_type_unexpected_parse_failure(
            ctx.document_name, base_path, base_type, "String")
        raise UApiSchemaParseError(
            this_parse_failures, ctx.uapi_schema_document_names_to_json)

    root_type_string = base_type

    regex_string = r"^(.+?)(\?)?$"
    regex = re.compile(regex_string)

    matcher = regex.match(root_type_string)
    if not matcher:
        raise UApiSchemaParseError([SchemaParseFailure(
            ctx.document_name, base_path, "StringRegexMatchFailed", {"regex": regex_string})], ctx.uapi_schema_document_names_to_json)

    type_name = matcher.group(1)
    nullable = bool(matcher.group(2))

    type_ = get_or_parse_type(base_path, type_name, ctx)

    given_type_parameter_count = len(type_declaration_array) - 1
    if type_.get_type_parameter_count() != given_type_parameter_count:
        raise UApiSchemaParseError([SchemaParseFailure(ctx.document_name, path, "ArrayLengthUnexpected",
                                                       {"actual": len(type_declaration_array),
                                                        "expected": type_.get_type_parameter_count() + 1})], ctx.uapi_schema_document_names_to_json)

    parse_failures = []
    type_parameters = []
    given_type_parameters = type_declaration_array[1:]

    for index, e in enumerate(given_type_parameters, start=1):
        loop_path = path + [index]

        if not isinstance(e, list):
            this_parse_failures = get_type_unexpected_parse_failure(
                ctx.document_name, loop_path, e, "Array")
            parse_failures.extend(this_parse_failures)
            continue

        try:
            type_parameter_type_declaration = parse_type_declaration(
                loop_path, e, ctx)

            type_parameters.append(type_parameter_type_declaration)
        except UApiSchemaParseError as e2:
            parse_failures.extend(e2.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(
            parse_failures, ctx.uapi_schema_document_names_to_json)

    return UTypeDeclaration(type_, nullable, type_parameters)
