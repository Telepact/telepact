from typing import List, Dict, Any, Set

from uapi.UApiSchemaParseError import UApiSchemaParseError
from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
from uapi.internal.schema.ParseTypeDeclaration import parse_type_declaration
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
from uapi.internal.types.UType import UType


def parse_headers_type(headers_definition_as_parsed_json: Dict[str, Any], schema_key: str,
                       header_field: str, index: int, uapi_schema_pseudo_json: List[Any],
                       schema_keys_to_index: Dict[str, int], parsed_types: Dict[str, 'UType'],
                       type_extensions: Dict[str, 'UType'], all_parse_failures: List['SchemaParseFailure'],
                       failed_types: Set[str]) -> 'UFieldDeclaration':
    path = [index, schema_key]

    type_declaration_value = headers_definition_as_parsed_json.get(schema_key)

    if not isinstance(type_declaration_value, list):
        raise UApiSchemaParseError(get_type_unexpected_parse_failure(
            path, type_declaration_value, "Array"))

    type_declaration_array = type_declaration_value

    type_parameter_count = 0

    try:
        type_declaration = parse_type_declaration(path, type_declaration_array, type_parameter_count,
                                                  uapi_schema_pseudo_json, schema_keys_to_index,
                                                  parsed_types, type_extensions, all_parse_failures, failed_types)

        return UFieldDeclaration(header_field, type_declaration, False)
    except UApiSchemaParseError as e:
        raise UApiSchemaParseError(e.schema_parse_failures)
