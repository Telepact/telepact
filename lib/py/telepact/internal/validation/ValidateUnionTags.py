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

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TStruct import TStruct
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_union_tags(reference_tags: dict[str, 'TStruct'], selected_tags: dict[str, object],
                        actual: dict[object, object], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ...internal.validation.ValidateUnionStruct import validate_union_struct

    if len(actual) != 1:
        return [
            ValidationFailure([], "ObjectSizeUnexpected", {
                              "actual": len(actual), "expected": 1})
        ]

    union_target, union_payload = cast(
        tuple[str, object], next(iter(actual.items())))

    reference_struct = reference_tags.get(union_target)
    if reference_struct is None:
        return [
            ValidationFailure([union_target], "ObjectKeyDisallowed", {})
        ]

    if isinstance(union_payload, dict):
        nested_validation_failures = validate_union_struct(reference_struct, union_target,
                                                           union_payload, selected_tags, ctx)

        nested_validation_failures_with_path = []
        for failure in nested_validation_failures:
            this_path = [union_target] + failure.path
            nested_validation_failures_with_path.append(
                ValidationFailure(this_path, failure.reason, failure.data)
            )

        return nested_validation_failures_with_path
    else:
        return get_type_unexpected_validation_failure([union_target], union_payload, "Object")
