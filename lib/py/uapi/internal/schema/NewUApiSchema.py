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

    final_pseudo_json: dict[str, list[object]] = {}

    for document_name, uapi_schema_json in uapi_schema_document_names_to_json.items():
        try:
            uapi_schema_pseudo_json_init = json.loads(uapi_schema_json)
        except json.JSONDecodeError as e:
            raise UApiSchemaParseError(
                [SchemaParseFailure(document_name, [], "JsonInvalid", {})]) from e

        if not isinstance(uapi_schema_pseudo_json_init, list):
            this_parse_failure = get_type_unexpected_parse_failure(
                document_name, [], uapi_schema_pseudo_json_init, "Array"
            )
            raise UApiSchemaParseError(this_parse_failure)

        uapi_schema_pseudo_json = uapi_schema_pseudo_json_init
        final_pseudo_json[document_name] = uapi_schema_pseudo_json

    return parse_uapi_schema(final_pseudo_json)
