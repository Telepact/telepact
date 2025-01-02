from typing import TYPE_CHECKING
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration

if TYPE_CHECKING:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    from uapi.internal.types.UType import UType


def parse_headers_type(document_name: str, headers_definition_as_parsed_json: dict[str, object], schema_key: str,
                       header_field: str, index: int, uapi_schema_document_names_to_pseudo_json: dict[str, list[object]],
                       schema_keys_to_document_names: dict[str, str], schema_keys_to_index: dict[str, int], parsed_types: dict[str, 'UType'],
                       all_parse_failures: list['SchemaParseFailure'],
                       failed_types: set[str]) -> 'UFieldDeclaration':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseTypeDeclaration import parse_type_declaration

    path = [index, schema_key]

    type_declaration_value = headers_definition_as_parsed_json.get(schema_key)

    if not isinstance(type_declaration_value, list):
        raise UApiSchemaParseError(get_type_unexpected_parse_failure(
            document_name, path, type_declaration_value, "Array"))

    type_declaration_array = type_declaration_value

    try:
        type_declaration = parse_type_declaration(document_name, path, type_declaration_array,
                                                  uapi_schema_document_names_to_pseudo_json,
                                                  schema_keys_to_document_names, schema_keys_to_index,
                                                  parsed_types, all_parse_failures, failed_types)

        return UFieldDeclaration(header_field, type_declaration, False)
    except UApiSchemaParseError as e:
        raise UApiSchemaParseError(e.schema_parse_failures)
