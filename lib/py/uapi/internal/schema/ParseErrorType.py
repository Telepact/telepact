from typing import TYPE_CHECKING, cast
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UError import UError

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType


def parse_error_type(error_definition_as_parsed_json: dict[str, object],
                     document_name: str,
                     u_api_schema_document_names_to_pseudo_json: dict[str, list[object]],
                     schema_key: str,
                     index: int,
                     schema_keys_to_document_names: dict[str, str],
                     schema_keys_to_index: dict[str, int],
                     parsed_types: dict[str, 'UType'],
                     all_parse_failures: list['SchemaParseFailure'],
                     failed_types: set[str]) -> 'UError':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ParseUnionType import parse_union_type

    base_path: list[object] = [index]

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if other_keys:
        for k in other_keys:
            loop_path = base_path + [k]
            parse_failures.append(SchemaParseFailure(
                document_name, cast(list[object], loop_path), "ObjectKeyDisallowed", {}))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    error = parse_union_type(document_name, base_path, error_definition_as_parsed_json, schema_key, [], [],
                             u_api_schema_document_names_to_pseudo_json, schema_keys_to_document_names, schema_keys_to_index,
                             parsed_types, all_parse_failures, failed_types)

    return UError(schema_key, error)
