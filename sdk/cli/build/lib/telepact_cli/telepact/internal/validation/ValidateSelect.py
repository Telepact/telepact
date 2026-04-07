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

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.validation.ValidationFailure import ValidationFailure


def validate_select(given_obj: object, possible_fn_selects: dict[str, object], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if not isinstance(given_obj, dict):
        return get_type_unexpected_validation_failure([], given_obj, 'Object')

    fn_scope = cast(str, ctx.fn)

    possible_select = possible_fn_selects[fn_scope]

    return is_sub_select([], given_obj, possible_select)


def is_sub_select(path: list[object], given_obj: object, possible_select_section: object) -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ...internal.validation.ValidationFailure import ValidationFailure

    if isinstance(possible_select_section, list):
        if not isinstance(given_obj, list):
            return get_type_unexpected_validation_failure(path, given_obj, 'Array')

        validation_failures = []

        for index, element in enumerate(given_obj):
            if element not in possible_select_section:
                validation_failures.append(ValidationFailure(
                    path + [index], 'ArrayElementDisallowed', {}))

        return validation_failures

    elif isinstance(possible_select_section, dict):
        if not isinstance(given_obj, dict):
            return get_type_unexpected_validation_failure(path, given_obj, 'Object')

        validation_failures = []

        for key, value in given_obj.items():
            if key in possible_select_section:
                inner_failures = is_sub_select(
                    path + [key], value, possible_select_section[key])
                validation_failures.extend(inner_failures)
            else:
                validation_failures.append(ValidationFailure(
                    path + [key], 'ObjectKeyDisallowed', {}))

        return validation_failures

    return []
