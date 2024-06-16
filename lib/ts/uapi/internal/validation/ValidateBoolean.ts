from typing import TYPE_CHECKING
from uapi.internal.types.UBoolean import _BOOLEAN_NAME

if TYPE_CHECKING:
    from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_boolean(value: object) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, bool):
        return []
    else:
        return get_type_unexpected_validation_failure([], value, _BOOLEAN_NAME)
