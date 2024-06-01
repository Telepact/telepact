from typing import List, Union
from uapi.internal.types import UString
from uapi.internal.validation import GetTypeUnexpectedValidationFailure


def validate_string(value: Union[str, object]) -> List[ValidationFailure]:
    if isinstance(value, str):
        return []
    else:
        return GetTypeUnexpectedValidationFailure([], value, UString._STRING_NAME)
