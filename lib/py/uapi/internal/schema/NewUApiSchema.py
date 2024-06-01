from typing import List, Dict
import json
from uapi import UApiSchema, UApiSchemaParseError
from uapi.internal.types import UType
from uapi.internal.schema import GetTypeUnexpectedParseFailure, ParseUApiSchema


def new_uapi_schema(uapi_schema_json: str, type_extensions: Dict[str, UType]) -> UApiSchema:
    uapi_schema_pseudo_json_init = json.loads(uapi_schema_json)

    if not isinstance(uapi_schema_pseudo_json_init, list):
        this_parse_failure = GetTypeUnexpectedParseFailure.get_type_unexpected_parse_failure(
            [], uapi_schema_pseudo_json_init, "Array"
        )
        raise UApiSchemaParseError(this_parse_failure)

    uapi_schema_pseudo_json = uapi_schema_pseudo_json_init

    return ParseUApiSchema.parse_uapi_schema(uapi_schema_pseudo_json, type_extensions, 0)
