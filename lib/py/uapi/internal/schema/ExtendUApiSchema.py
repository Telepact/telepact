from typing import List, Dict
import json
from uapi import UApiSchema, UApiSchemaParseError, UType
from uapi.internal.schema import GetTypeUnexpectedParseFailure, ParseUApiSchema


def extend_uapi_schema(first: UApiSchema, second_uapi_schema_json: str,
                       second_type_extensions: Dict[str, UType]) -> UApiSchema:
    second_uapi_schema_pseudo_json_init = json.loads(second_uapi_schema_json)

    if not isinstance(second_uapi_schema_pseudo_json_init, list):
        this_parse_failure = GetTypeUnexpectedParseFailure.get_type_unexpected_parse_failure(
            [], second_uapi_schema_pseudo_json_init, "Array"
        )
        raise UApiSchemaParseError(this_parse_failure)

    second_uapi_schema_pseudo_json = second_uapi_schema_pseudo_json_init

    first_original = first.original
    first_type_extensions = first.type_extensions

    original = first_original + second_uapi_schema_pseudo_json

    type_extensions = {**first_type_extensions, **second_type_extensions}

    return ParseUApiSchema.parse_uapi_schema(original, type_extensions, len(first_original))
