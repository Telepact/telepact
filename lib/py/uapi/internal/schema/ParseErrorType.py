from typing import TYPE_CHECKING, cast
from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
from uapi.internal.types.UError import UError

if TYPE_CHECKING:
    from uapi.internal.schema.ParseContext import ParseContext


def parse_error_type(error_definition_as_parsed_json: dict[str, object],
                     schema_key: str,
                     ctx: 'ParseContext') -> 'UError':
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.ParseUnionType import parse_union_type

    parse_failures = []

    other_keys = set(error_definition_as_parsed_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")

    if other_keys:
        for k in other_keys:
            loop_path = ctx.path + [k]
            parse_failures.append(SchemaParseFailure(
                ctx.document_name, cast(list[object], loop_path), "ObjectKeyDisallowed", {}))

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)

    error = parse_union_type(error_definition_as_parsed_json, schema_key, [], [],
                             ctx)

    return UError(schema_key, error)
