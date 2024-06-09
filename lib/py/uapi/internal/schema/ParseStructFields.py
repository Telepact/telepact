from typing import List, Dict, Any, Set, TYPE_CHECKING

from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

if TYPE_CHECKING:
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UType import UType


def parse_struct_fields(reference_struct: Dict[str, Any], path: List[Any], type_parameter_count: int,
                        uapi_schema_pseudo_json: List[Any], schema_keys_to_index: Dict[str, int],
                        parsed_types: Dict[str, 'UType'], type_extensions: Dict[str, 'UType'],
                        all_parse_failures: List['SchemaParseFailure'], failed_types: Set[str]) -> Dict[str, 'UFieldDeclaration']:
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ParseField import parse_field

    parse_failures = []
    fields = {}

    for field_declaration, type_declaration_value in reference_struct.items():
        for existing_field in fields.keys():
            existing_field_no_opt = existing_field.split("!")[0]
            field_no_opt = field_declaration.split("!")[0]
            if field_no_opt == existing_field_no_opt:
                final_path = path + [field_declaration]
                final_other_path = path + [existing_field]
                parse_failures.append(SchemaParseFailure(
                    final_path, "PathCollision", {"other": final_other_path}, None))

        try:
            parsed_field = parse_field(path, field_declaration, type_declaration_value, type_parameter_count,
                                       uapi_schema_pseudo_json, schema_keys_to_index, parsed_types,
                                       type_extensions, all_parse_failures, failed_types)
            field_name = parsed_field.field_name
            fields[field_name] = parsed_field
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    return fields
