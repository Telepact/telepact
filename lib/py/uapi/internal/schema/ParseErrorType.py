from typing import List, Dict, Any, Union, Set
from uapi import UApiSchemaParseError
from uapi.internal.types import UError, UType, UUnion
from uapi.internal.schema import ParseUnionType


def parse_error_type(error_definition_as_parsed_json: Dict[str, Any],
                     u_api_schema_pseudo_json: List[Any],
                     index: int,
                     schema_keys_to_index: Dict[str, int],
                     parsed_types: Dict[str, UType],
                     type_extensions: Dict[str, UType],
                     all_parse_failures: List[SchemaParseFailure],
                     failed_types: Set[str]) -> UError:
    schema_key = "errors"
    base_path = [index]

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.remove(schema_key)
    other_keys.remove("///")

    if other_keys:
        for k in other_keys:
            loop_path = base_path + [k]
            parse_failures.append(SchemaParseFailure(
                loop_path, "ObjectKeyDisallowed", {}, None))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    type_parameter_count = 0

    error = ParseUnionType.parse_union_type(base_path, error_definition_as_parsed_json, schema_key, [], [],
                                            type_parameter_count, u_api_schema_pseudo_json, schema_keys_to_index,
                                            parsed_types, type_extensions, all_parse_failures, failed_types)

    return UError(schema_key, error)
