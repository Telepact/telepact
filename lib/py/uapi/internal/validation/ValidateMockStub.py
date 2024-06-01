from typing import Any, Dict, List, Union

from uapi.internal.types.UFn import UFn
from uapi.internal.types.UStruct import UStruct
from uapi.internal.types.UType import UType
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
from uapi.internal.types.UUnion import UUnion
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_mock_stub(given_obj: Any, select: Dict[str, Any], fn: str,
                       type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                       types: Dict[str, 'UType']) -> List['ValidationFailure']:
    validation_failures: List[ValidationFailure] = []

    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    given_map: Dict[str, Any] = given_obj

    regex_string = "^fn\\..*$"

    keys = sorted(given_map.keys())

    matches = [k for k in keys if re.match(regex_string, k)]
    if len(matches) != 1:
        return [
            ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected",
                              {"regex": regex_string, "actual": len(matches), "expected": 1, "keys": keys})
        ]

    function_name = matches[0]
    function_def: UFn = types[function_name]
    input = given_map[function_name]

    function_def_call: UUnion = function_def.call
    function_def_name: str = function_def.name
    function_def_call_cases: Dict[str, UStruct] = function_def_call.cases
    input_failures = function_def_call_cases[function_def_name].validate(
        input, select, fn, [], [])

    input_failures_with_path = []
    for f in input_failures:
        this_path = [function_name] + f.path

        input_failures_with_path.append(
            ValidationFailure(this_path, f.reason, f.data))

    input_failures_without_missing_required = [
        f for f in input_failures_with_path if f.reason != "RequiredObjectKeyMissing"
    ]

    validation_failures.extend(input_failures_without_missing_required)

    result_def_key = "->"

    if result_def_key not in given_map:
        validation_failures.append(ValidationFailure(
            [result_def_key], "RequiredObjectKeyMissing", {}))
    else:
        output = given_map[result_def_key]
        output_failures = function_def.result.validate(
            output, select, fn, [], [])

        output_failures_with_path = []
        for f in output_failures:
            this_path = [result_def_key] + f.path

            output_failures_with_path.append(
                ValidationFailure(this_path, f.reason, f.data))

        failures_without_missing_required = [
            f for f in output_failures_with_path if f.reason != "RequiredObjectKeyMissing"
        ]

        validation_failures.extend(failures_without_missing_required)

    disallowed_fields = [k for k in given_map.keys(
    ) if k not in matches and k != result_def_key]
    for disallowed_field in disallowed_fields:
        validation_failures.append(ValidationFailure(
            [disallowed_field], "ObjectKeyDisallowed", {}))

    return validation_failures
