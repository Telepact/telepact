from typing import List, Dict, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from uapi.UApiSchema import UApiSchema
    from uapi.internal.types.UType import UType


def new_uapi_schema(uapi_schema_json: str, type_extensions: Dict[str, 'UType']) -> 'UApiSchema':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseUApiSchema import parse_uapi_schema

    uapi_schema_pseudo_json_init = json.loads(uapi_schema_json)

    if not isinstance(uapi_schema_pseudo_json_init, list):
        this_parse_failure = get_type_unexpected_parse_failure(
            [], uapi_schema_pseudo_json_init, "Array"
        )
        raise UApiSchemaParseError(this_parse_failure)

    uapi_schema_pseudo_json = uapi_schema_pseudo_json_init

    return parse_uapi_schema(uapi_schema_pseudo_json, type_extensions, 0)
