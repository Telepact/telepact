from typing import TYPE_CHECKING, cast
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ..types.VError import VError

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext


def parse_error_type(path: list[object], error_definition_as_parsed_json: dict[str, object],
                     schema_key: str,
                     ctx: 'ParseContext') -> 'VError':
    from ...TelepactSchemaParseError import TelepactSchemaParseError
    from ...internal.schema.ParseUnionType import parse_union_type

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                ctx.document_name, cast(list[object], loop_path), "ObjectKeyDisallowed", {}))

    if parse_failures:
        raise TelepactSchemaParseError(
            parse_failures, ctx.telepact_schema_document_names_to_json)

    error = parse_union_type(path, error_definition_as_parsed_json, schema_key, [], [],
                             ctx)

    return VError(schema_key, error)
