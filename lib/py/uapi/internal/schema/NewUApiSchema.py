from typing import TYPE_CHECKING
import json


if TYPE_CHECKING:
    from uapi.UApiSchema import UApiSchema
    from uapi.internal.types.UType import UType


def new_uapi_schema(uapi_schema_document_names_to_json: dict[str, str]) -> 'UApiSchema':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from uapi.internal.schema.ParseUApiSchema import parse_uapi_schema
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure

    return parse_uapi_schema(uapi_schema_document_names_to_json)
