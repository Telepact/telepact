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
    from ..types.TTypeDeclaration import TTypeDeclaration
    from ..types.TType import TType


def validate_mock_call(given_obj: object, types: dict[str, 'TType'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ..types.TUnion import TUnion

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
    function_def = cast(TUnion, types[function_name])
    input = given_map[function_name]

    function_def_call = function_def
    function_def_name = function_name
    function_def_call_tags = function_def_call.tags

    input_failures = function_def_call_tags[function_def_name].validate(
        input, [], ctx)

    input_failures_with_path = []
    for f in input_failures:
        new_path = [function_name] + f.path

        input_failures_with_path.append(
            ValidationFailure(new_path, f.reason, f.data))

    return [f for f in input_failures_with_path if f.reason != "RequiredObjectKeyMissing"]
