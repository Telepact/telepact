from typing import list, object, dict

from uapi.internal.validation.ValidationFailure import ValidationFailure


def get_type_unexpected_validation_failure(path: list[object], value: object, expected_type: str) -> list['ValidationFailure']:
    from uapi.internal.types.GetType import get_type

    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        ValidationFailure(path, "TypeUnexpected", data)
    ]
