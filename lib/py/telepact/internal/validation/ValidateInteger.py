from ..types.VInteger import _INTEGER_NAME
from ...internal.validation.ValidationFailure import ValidationFailure


def validate_integer(value: object) -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, (int)) and not isinstance(value, (bool, float)):
        if (value > 2**63-1 or value < -(2**63)):
            return [ValidationFailure([], "NumberOutOfRange", {})]
        else:
            return []

    return get_type_unexpected_validation_failure([], value, _INTEGER_NAME)
