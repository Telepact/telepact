from typing import List
from uapi.internal.types import UBoolean
from uapi.internal.validation import GetTypeUnexpectedValidationFailure


def validate_boolean(value: object) -> List[ValidationFailure]:
    if isinstance(value, bool):
        return []
    else:
        return GetTypeUnexpectedValidationFailure([], value, UBoolean._BOOLEAN_NAME)
