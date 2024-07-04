from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from uapi.internal.types.UType import UType
    from uapi.UApiSchema import UApiSchema


def extend_uapi_schema(first: 'UApiSchema', second_uapi_schema_json: str) -> 'UApiSchema':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseUApiSchema import parse_uapi_schema
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

    try:
        second_uapi_schema_pseudo_json_init = json.loads(
            second_uapi_schema_json)
    except json.JSONDecodeError as e:
        raise UApiSchemaParseError(
            [SchemaParseFailure([], "JsonInvalid", {}, None)]) from e

    if not isinstance(second_uapi_schema_pseudo_json_init, list):
        this_parse_failure = get_type_unexpected_parse_failure(
            [], second_uapi_schema_pseudo_json_init, "Array"
        )
        raise UApiSchemaParseError(this_parse_failure)

    second_uapi_schema_pseudo_json = second_uapi_schema_pseudo_json_init

    first_original = first.original

    original = first_original + second_uapi_schema_pseudo_json

    return parse_uapi_schema(original, len(first_original))
