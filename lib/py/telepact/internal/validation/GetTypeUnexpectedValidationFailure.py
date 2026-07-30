#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from ...internal.validation.ValidationFailure import ValidationFailure
from ...internal.types.GetType import get_type


def get_type_unexpected_validation_failure(path: list[object], value: object, expected_type: str) -> list['ValidationFailure']:
    actual_type = get_type(value)
    data: dict[str, object] = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        ValidationFailure(path, "TypeUnexpected", data)
    ]
