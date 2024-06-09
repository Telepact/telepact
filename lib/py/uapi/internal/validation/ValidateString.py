from typing import list, Union
from uapi.internal.types.UString import _STRING_NAME
from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_string(value: Union[str, object]) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, str):
        return []
    else:
        return get_type_unexpected_validation_failure([], value, _STRING_NAME)
