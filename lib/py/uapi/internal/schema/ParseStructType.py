from typing import List, Dict, Any, Set

from uapi.UApiSchemaParseError import UApiSchemaParseError
from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
from uapi.internal.schema.ParseStructFields import parse_struct_fields
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UStruct import UStruct
from uapi.internal.types.UType import UType


def parse_struct_type(path: List[Any], struct_definition_as_pseudo_json: Dict[str, Any],
                      schema_key: str, ignore_keys: List[str], type_parameter_count: int,
                      uapi_schema_pseudo_json: List[Any], schema_keys_to_index: Dict[str, int],
                      parsed_types: Dict[str, UType], type_extensions: Dict[str, UType],
                      all_parse_failures: List[SchemaParseFailure], failed_types: Set[str]) -> UStruct:
    parse_failures = []
    other_keys = set(struct_definition_as_pseudo_json.keys())

    other_keys.remove(schema_key)
    other_keys.remove("///")
    other_keys.remove("_ignore_if_duplicate")
    for ignore_key in ignore_keys:
        other_keys.remove(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                loop_path, "ObjectKeyDisallowed", {}, None))

    this_path = path + [schema_key]
    def_init = struct_definition_as_pseudo_json.get(schema_key)

    definition = None
    if not isinstance(def_init, dict):
        branch_parse_failures = get_type_unexpected_parse_failure(
            this_path, def_init, "Object")
        parse_failures.extend(branch_parse_failures)
    else:
        definition = def_init

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    fields = parse_struct_fields(definition, this_path, type_parameter_count, uapi_schema_pseudo_json,
                                 schema_keys_to_index, parsed_types, type_extensions, all_parse_failures,
                                 failed_types)

    return UStruct(schema_key, fields, type_parameter_count)
