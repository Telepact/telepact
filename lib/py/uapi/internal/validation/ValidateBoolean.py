from typing import List
from uapi.internal.types.UBoolean import _BOOLEAN_NAME
from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_boolean(value: object) -> List['ValidationFailure']:
    if isinstance(value, bool):
        return []
    else:
        return get_type_unexpected_validation_failure([], value, _BOOLEAN_NAME)
