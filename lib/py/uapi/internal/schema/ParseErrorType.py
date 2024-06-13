from typing import TYPE_CHECKING, cast
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UError import UError

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def parse_error_type(error_definition_as_parsed_json: dict[str, object],
                     u_api_schema_pseudo_json: list[object],
                     index: int,
                     schema_keys_to_index: dict[str, int],
                     parsed_types: dict[str, 'UType'],
                     type_extensions: dict[str, 'UType'],
                     all_parse_failures: list['SchemaParseFailure'],
                     failed_types: set[str]) -> 'UError':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ParseUnionType import parse_union_type

    schema_key = "errors"
    base_path: list[object] = [index]

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if other_keys:
        for k in other_keys:
            loop_path = base_path + [k]
            parse_failures.append(SchemaParseFailure(
                cast(list[object], loop_path), "ObjectKeyDisallowed", {}, None))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    type_parameter_count = 0

    error = parse_union_type(base_path, error_definition_as_parsed_json, schema_key, [], [],
                             type_parameter_count, u_api_schema_pseudo_json, schema_keys_to_index,
                             parsed_types, type_extensions, all_parse_failures, failed_types)

    return UError(schema_key, error)
