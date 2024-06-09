from typing import List, Any, Dict

from uapi.internal.validation.ValidationFailure import ValidationFailure


def get_type_unexpected_validation_failure(path: List[Any], value: Any, expected_type: str) -> List['ValidationFailure']:
    from uapi.internal.types.GetType import get_type

    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        ValidationFailure(path, "TypeUnexpected", data)
    ]
