import re
from typing import list, dict, object, Set, TYPE_CHECKING
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def parse_field(path: list[object], field_declaration: str, type_declaration_value: object,
                type_parameter_count: int, uapi_schema_pseudo_json: list[object],
                schema_keys_to_index: dict[str, int], parsed_types: dict[str, 'UType'],
                type_extensions: dict[str, 'UType'], all_parse_failures: list['SchemaParseFailure'],
                failed_types: Set[str]) -> 'UFieldDeclaration':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseTypeDeclaration import parse_type_declaration

    regex_string = r"^([a-z][a-zA-Z0-9_]*)(!)?$"
    regex = re.compile(regex_string)

    matcher = regex.match(field_declaration)
    if not matcher:
        final_path = path + [field_declaration]
        raise UApiSchemaParseError([SchemaParseFailure(final_path,
                                                       "KeyRegexMatchFailed",
                                                       {"regex": regex_string},
                                                       None)])

    field_name = matcher.group(0)
    optional = bool(matcher.group(2))

    this_path = path + [field_name]

    if not isinstance(type_declaration_value, list):
        raise UApiSchemaParseError(get_type_unexpected_parse_failure(this_path,
                                                                     type_declaration_value,
                                                                     "Array"))
    type_declaration_array = type_declaration_value

    type_declaration = parse_type_declaration(this_path,
                                              type_declaration_array,
                                              type_parameter_count,
                                              uapi_schema_pseudo_json,
                                              schema_keys_to_index,
                                              parsed_types,
                                              type_extensions,
                                              all_parse_failures,
                                              failed_types)

    return UFieldDeclaration(field_name, type_declaration, optional)
