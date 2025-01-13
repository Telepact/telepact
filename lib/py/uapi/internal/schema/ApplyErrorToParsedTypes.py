import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.types.UError import UError
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UUnion import UUnion


def apply_error_to_parsed_types(error: 'UError', parsed_types: dict[str, 'UType'], schema_keys_to_document_names: dict[str, str], schema_keys_to_index: dict[str, int], document_names_to_json: dict[str, str]) -> None:
    from uapi.internal.schema.SchemaParseFailure import SchemaParseFailure
    from uapi.UApiSchemaParseError import UApiSchemaParseError
    from uapi.internal.schema.GetPathDocumentCoordinatesPseudoJson import get_path_document_coordinates_pseudo_json
    from uapi.internal.types.UFn import UFn

    parse_failures = []

    error_key = error.name
    error_index = schema_keys_to_index[error_key]
    document_name = schema_keys_to_document_names[error_key]

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

        matcher = regex.match(error_key)
        if not matcher:
            continue

        for error_case_name, error_case in error_cases.items():
            new_key = error_case_name

            if new_key in fn_result_cases:
                other_path_index = schema_keys_to_index[fn_name]
                error_case_index = error.errors.case_indices[new_key]
                other_document_name = schema_keys_to_document_names[fn_name]
                fn_error_case_index = f.result.case_indices[new_key]
                other_final_path = [other_path_index,
                                    "->", fn_error_case_index, new_key]
                other_document_json = document_names_to_json[other_document_name]
                other_location_pseudo_json = get_path_document_coordinates_pseudo_json(
                    other_final_path, other_document_json)
                parse_failures.append(SchemaParseFailure(
                    document_name,
                    [error_index, error_key,
                     error_case_index, new_key],
                    "PathCollision",
                    {"document": other_document_name,
                     "path": other_final_path,
                        "location": other_location_pseudo_json}
                ))
            fn_result_cases[new_key] = error_case

    if parse_failures:
        raise UApiSchemaParseError(
            parse_failures, document_names_to_json)
