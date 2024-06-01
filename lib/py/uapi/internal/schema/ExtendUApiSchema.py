from typing import List, Dict
import json
from uapi.UApiSchema import UApiSchema
from uapi.UApiSchemaParseError import UApiSchemaParseError
from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
from uapi.internal.types.UType import UType
from uapi.internal.schema.ParseUApiSchema import parse_uapi_schema


def extend_uapi_schema(first: 'UApiSchema', second_uapi_schema_json: str,
                       second_type_extensions: Dict[str, 'UType']) -> 'UApiSchema':
    second_uapi_schema_pseudo_json_init = json.loads(second_uapi_schema_json)

    if not isinstance(second_uapi_schema_pseudo_json_init, list):
        this_parse_failure = get_type_unexpected_parse_failure(
            [], second_uapi_schema_pseudo_json_init, "Array"
        )
        raise UApiSchemaParseError(this_parse_failure)

    second_uapi_schema_pseudo_json = second_uapi_schema_pseudo_json_init

    first_original = first.original
    first_type_extensions = first.type_extensions

    original = first_original + second_uapi_schema_pseudo_json

    type_extensions = {**first_type_extensions, **second_type_extensions}

    return parse_uapi_schema(original, type_extensions, len(first_original))
