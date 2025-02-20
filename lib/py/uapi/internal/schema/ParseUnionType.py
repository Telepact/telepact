import re
from typing import TYPE_CHECKING
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ...internal.types.UUnion import UUnion

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ...internal.types.UType import UType


def parse_union_type(path: list[object], union_definition_as_pseudo_json: dict[str, object], schema_key: str,
                     ignore_keys: list[str], required_keys: list[str],
                     ctx: 'ParseContext') -> 'UUnion':
    from ...UApiSchemaParseError import UApiSchemaParseError
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ...internal.schema.ParseStructFields import parse_struct_fields
    from ...internal.types.UStruct import UStruct

    parse_failures = []

    other_keys = set(union_definition_as_pseudo_json.keys())
    other_keys.discard(schema_key)
    other_keys.discard("///")
    for ignore_key in ignore_keys:
        other_keys.discard(ignore_key)

    if other_keys:
        for k in other_keys:
            loop_path = path + [k]
            parse_failures.append(SchemaParseFailure(
                ctx.document_name, loop_path, "ObjectKeyDisallowed", {}))

    this_path = path + [schema_key]
    def_init = union_definition_as_pseudo_json[schema_key]

    if not isinstance(def_init, list):
        final_parse_failures = get_type_unexpected_parse_failure(
            ctx.document_name, this_path, def_init, "Array")
        parse_failures.extend(final_parse_failures)
        raise UApiSchemaParseError(
            parse_failures, ctx.uapi_schema_document_names_to_json)

    definition2 = def_init
    definition = []
    index = -1
    for element in definition2:
        index += 1
        loop_path = this_path + [index]
        if not isinstance(element, dict):
            this_parse_failures = get_type_unexpected_parse_failure(
                ctx.document_name, loop_path, element, "Object")
            parse_failures.extend(this_parse_failures)
            continue
        definition.append(element)

    if parse_failures:
        raise UApiSchemaParseError(
            parse_failures, ctx.uapi_schema_document_names_to_json)

    if len(definition) == 0:
        parse_failures.append(SchemaParseFailure(
            ctx.document_name, this_path, "EmptyArrayDisallowed", {}))
    else:
        for required_key in required_keys:
            for element in definition:
                tag_keys = set(element.keys())
                tag_keys.discard("///")
                if required_key in tag_keys:
                    break
            else:
                branch_path = this_path + [0]
                parse_failures.append(SchemaParseFailure(
                    ctx.document_name, branch_path, "RequiredObjectKeyMissing", {'key': required_key}))

    tags = {}
    tag_indices = {}

    for i, element in enumerate(definition):
        loop_path = this_path + [i]
        map_init = element
        map = dict(map_init)
        map.pop("///", None)
        keys = list(map.keys())

        regex_string = r"^([A-Z][a-zA-Z0-9_]*)$"

        matches = [k for k in keys if re.match(regex_string, k)]
        if len(matches) != 1:
            parse_failures.append(SchemaParseFailure(ctx.document_name, loop_path, "ObjectKeyRegexMatchCountUnexpected",
                                                     {"regex": regex_string, "actual": len(matches),
                                                      "expected": 1, "keys": keys}))
            continue
        if len(map) != 1:
            parse_failures.append(SchemaParseFailure(ctx.document_name, loop_path, "ObjectSizeUnexpected",
                                                     {"expected": 1, "actual": len(map)}))
            continue

        entry = next(iter(map.items()))
        union_tag = entry[0]
        union_key_path = loop_path + [union_tag]

        if not isinstance(entry[1], dict):
            this_parse_failures = get_type_unexpected_parse_failure(
                ctx.document_name, union_key_path, entry[1], "Object")
            parse_failures.extend(this_parse_failures)
            continue
        union_tag_struct = entry[1]

        try:
            fields = parse_struct_fields(union_key_path,
                                         union_tag_struct, ctx)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)
            continue

        union_struct = UStruct(
            f"{schema_key}.{union_tag}", fields)

        tags[union_tag] = union_struct
        tag_indices[union_tag] = i

    if parse_failures:
        raise UApiSchemaParseError(
            parse_failures, ctx.uapi_schema_document_names_to_json)

    return UUnion(schema_key, tags, tag_indices)
