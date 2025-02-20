from typing import TYPE_CHECKING, cast
from ...internal.schema.DerivePossibleSelects import derive_possible_select
from ...internal.schema.GetOrParseType import get_or_parse_type
from ...internal.schema.SchemaParseFailure import SchemaParseFailure
from ...internal.types.USelect import USelect
from ...internal.types.UFn import UFn

if TYPE_CHECKING:
    from ...internal.schema.ParseContext import ParseContext
    from ...internal.types.UType import UType


def parse_function_type(path: list[object], function_definition_as_parsed_json: dict[str, object],
                        schema_key: str,
                        ctx: 'ParseContext') -> 'UFn':
    from ...internal.schema.GetTypeUnexpectedParseFailure import get_type_unexpected_parse_failure
    from ...internal.schema.ParseStructType import parse_struct_type
    from ...internal.schema.ParseUnionType import parse_union_type
    from ...internal.schema.ParseUnionType import parse_union_type
    from ...UApiSchemaParseError import UApiSchemaParseError
    from ...internal.schema.SchemaParseFailure import SchemaParseFailure
    from ...internal.types.UUnion import UUnion

    parse_failures = []

    call_type = None
    try:
        arg_type = parse_struct_type(path, function_definition_as_parsed_json,
                                     schema_key, ["->", "_errors"],
                                     ctx)
        call_type = UUnion(schema_key, {schema_key: arg_type}, {
                           schema_key: 0})
    except UApiSchemaParseError as e:
        parse_failures.extend(e.schema_parse_failures)

    result_schema_key = "->"

    result_type = None
    if result_schema_key not in function_definition_as_parsed_json:
        parse_failures.append(SchemaParseFailure(
            ctx.document_name, path, "RequiredObjectKeyMissing", {'key': result_schema_key}))
    else:
        try:
            result_type = parse_union_type(path, function_definition_as_parsed_json,
                                           result_schema_key, list(
                                               function_definition_as_parsed_json.keys()),
                                           ["Ok_"], ctx)
        except UApiSchemaParseError as e:
            parse_failures.extend(e.schema_parse_failures)

    errors_regex_key = "_errors"

    regex_path = path + [errors_regex_key]

    errors_regex = None
    if errors_regex_key in function_definition_as_parsed_json and not schema_key.endswith("_"):
        parse_failures.append(SchemaParseFailure(
            ctx.document_name, regex_path, "ObjectKeyDisallowed", {}))
    else:
        errors_regex_init = function_definition_as_parsed_json.get(
            errors_regex_key, "^errors\\..*$")

        if not isinstance(errors_regex_init, str):
            this_parse_failures = get_type_unexpected_parse_failure(
                ctx.document_name, regex_path, errors_regex_init, "String")
            parse_failures.extend(this_parse_failures)
        else:
            errors_regex = errors_regex_init

    if parse_failures:
        raise UApiSchemaParseError(
            parse_failures, ctx.uapi_schema_document_names_to_json)

    fn_select_type = derive_possible_select(
        schema_key, cast(UUnion, result_type))
    select_type = cast(USelect, get_or_parse_type([], '_ext.Select_', ctx))
    select_type.possible_selects[schema_key] = fn_select_type

    return UFn(schema_key, cast(UUnion, call_type), cast(UUnion, result_type), cast(str, errors_regex))
