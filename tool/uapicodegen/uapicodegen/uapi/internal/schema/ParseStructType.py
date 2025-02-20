from typing import TYPE_CHECKING, cast
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ...internal.types.UStruct import UStruct

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ...internal.types.UType import UType


def parse_struct_type(path: list[object], struct_definition_as_pseudo_json: dict[str, object],
                      schema_key: str, ignore_keys: list[str],
                      ctx: 'ParseContext') -> 'UStruct':
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ...internal.schema.ParseStructFields import parse_struct_fields
    from ...UApiSchemaParseError import UApiSchemaParseError

    parse_failures = []
    other_keys = set(struct_definition_as_pseudo_json.keys())

    other_keys.discard(schema_key)
    other_keys.discard("///")
    other_keys.discard("_ignoreIfDuplicate")
    for ignore_key in ignore_keys:
        other_keys.discard(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                ctx.document_name, loop_path, "ObjectKeyDisallowed", {}))

    this_path = path + [schema_key]
    def_init = cast(dict[str, object],
                    struct_definition_as_pseudo_json.get(schema_key))

    definition = None
    if not isinstance(def_init, dict):
        branch_parse_failures = get_type_unexpected_parse_failure(
            ctx.document_name, this_path, def_init, "Object")
        parse_failures.extend(branch_parse_failures)
    else:
        definition = def_init

    if parse_failures:
        raise UApiSchemaParseError(
            parse_failures, ctx.uapi_schema_document_names_to_json)

    fields = parse_struct_fields(this_path, definition, ctx)

    return UStruct(schema_key, fields)
