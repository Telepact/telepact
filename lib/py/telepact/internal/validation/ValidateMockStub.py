#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING, cast
from ...internal.validation.ValidationFailure import ValidationFailure

import re

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TStruct import TStruct
    from ..types.TType import TType


def validate_mock_stub(given_obj: object,
                       types: dict[str, 'TType'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ..types.TUnion import TUnion

    validation_failures: list[ValidationFailure] = []

    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, "Object")

    given_map: dict[str, object] = given_obj

    regex_string = "^fn\\..*$"

    keys = sorted(given_map.keys())

    matches = [k for k in keys if re.match(regex_string, k)]
    if len(matches) != 1:
        return [
            ValidationFailure([], "ObjectKeyRegexMatchCountUnexpected",
                              {"regex": regex_string, "actual": len(matches), "expected": 1, "keys": keys})
        ]

    function_name = matches[0]
    input = given_map[function_name]

    function_def_call = cast(TUnion, types[function_name])
    function_def_result = cast(TUnion, types[function_name + '.->'])
    function_def_name: str = function_name
    function_def_call_tags: dict[str, TStruct] = function_def_call.tags
    input_failures = function_def_call_tags[function_def_name].validate(
        input, [], ctx)

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
            [], "RequiredObjectKeyMissing", {'key': result_def_key}))
    else:
        output = given_map[result_def_key]
        output_failures = function_def_result.validate(
            output, [], ctx)

        output_failures_with_path: list[ValidationFailure] = []
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
