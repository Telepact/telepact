import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.types.UError import UError
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UUnion import UUnion


def apply_error_to_parsed_types(error_key: str, error_index: int, error: 'UError', parsed_types: dict[str, 'UType'], schema_keys_to_index: dict[str, int]) -> None:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.types.UFn import UFn

    parse_failures = []
    for parsed_type_name, parsed_type in parsed_types.items():
        if not isinstance(parsed_type, UFn):
            continue
        f = parsed_type

        fn_name = f.name

        regex = re.compile(f.errors_regex)

        fn_result = f.result
        fn_result_cases = fn_result.cases
        error_errors = error.errors
        error_cases = error_errors.cases

        for error_case_name, error_case in error_cases.items():
            new_key = error_case_name

            matcher = regex.match(new_key)
            if not matcher:
                continue

            if new_key in fn_result_cases:
                other_path_index = schema_keys_to_index[fn_name]
                error_case_index = error.errors.case_indices[new_key]
                fn_error_case_index = f.result.case_indices[new_key]
                parse_failures.append(SchemaParseFailure(
                    [error_index, error_key, error_case_index, new_key],
                    "PathCollision",
                    {"other": [other_path_index, "->",
                               fn_error_case_index, new_key]},
                    None
                ))
            fn_result_cases[new_key] = error_case

    if parse_failures:
        raise UApiSchemaParseError(parse_failures)
