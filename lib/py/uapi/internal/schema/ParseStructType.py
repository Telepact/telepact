from typing import TYPE_CHECKING, cast
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UStruct import UStruct

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def parse_struct_type(document_name: str, path: list[object], struct_definition_as_pseudo_json: dict[str, object],
                      schema_key: str, ignore_keys: list[str], type_parameter_count: int,
                      uapi_schema_document_names_to_pseudo_json: dict[str, list[object]],
                      schema_keys_to_document_name: dict[str, str], schema_keys_to_index: dict[str, int],
                      parsed_types: dict[str, 'UType'],
                      all_parse_failures: list['SchemaParseFailure'], failed_types: set[str]) -> 'UStruct':
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseStructFields import parse_struct_fields
    from uapi.UApiSchemaParseError import UApiSchemaParseError

    parse_failures = []
    other_keys = set(struct_definition_as_pseudo_json.keys())

    other_keys.discard(schema_key)
    other_keys.discard("///")
    other_keys.discard("_ignoreIfDuplicate")
    for ignore_key in ignore_keys:
        other_keys.discard(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                document_name, loop_path, "ObjectKeyDisallowed", {}))

    this_path = path + [schema_key]
    def_init = cast(dict[str, object],
                    struct_definition_as_pseudo_json.get(schema_key))

    definition = None
    if not isinstance(def_init, dict):
        branch_parse_failures = get_type_unexpected_parse_failure(
            document_name, this_path, def_init, "Object")
        parse_failures.extend(branch_parse_failures)
    else:
        definition = def_init

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    fields = parse_struct_fields(definition, document_name, this_path, type_parameter_count, uapi_schema_document_names_to_pseudo_json,
                                 schema_keys_to_document_name, schema_keys_to_index, parsed_types, all_parse_failures,
                                 failed_types)

    return UStruct(schema_key, fields, type_parameter_count)
