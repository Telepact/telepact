from typing import TYPE_CHECKING, cast
from uapi.internal.validation.ValidationFailure import ValidationFailure
import re

if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.types.UType import UType


def validate_mock_call(given_obj: object, types: dict[str, 'UType'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.types.UFn import UFn

    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    given_map = given_obj

    regex_string = "^fn\\..*$"

    keys = sorted(given_map.keys())

    matches = [k for k in keys if re.match(regex_string, k)]
    if len(matches) != 1:
        return [ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected",
                                  {"regex": regex_string, "actual": len(matches), "expected": 1, "keys": keys})]

    function_name = matches[0]
    function_def = cast(UFn, types[function_name])
    input = given_map[function_name]

    function_def_call = function_def.call
    function_def_name = function_def.name
    function_def_call_cases = function_def_call.cases

    input_failures = function_def_call_cases[function_def_name].validate(
        input, [], ctx)

    input_failures_with_path = []
    for f in input_failures:
        new_path = [function_name] + f.path

        input_failures_with_path.append(
            ValidationFailure(new_path, f.reason, f.data))

    return [f for f in input_failures_with_path if f.reason != "RequiredObjectKeyMissing"]
