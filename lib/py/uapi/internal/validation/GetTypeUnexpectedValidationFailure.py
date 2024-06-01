from typing import List, Any, Dict
from uapi.internal.types import get_type
from uapi.internal.validation import ValidationFailure


def get_type_unexpected_validation_failure(path: List[Any], value: Any, expected_type: str) -> List[ValidationFailure]:
    actual_type = get_type(value)
    data = {
        "actual": {actual_type: {}},
        "expected": {expected_type: {}}
    }
    return [
        ValidationFailure(path, "TypeUnexpected", data)
    ]
