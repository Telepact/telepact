from ...internal.types.UNumber import _NUMBER_NAME
from ...internal.validation.ValidationFailure import ValidationFailure


def validate_number(value: object) -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, (int, float)) and not isinstance(value, (bool, str)):
        if isinstance(value, (int)):
            if (value > 2**63-1 or value < -(2**63)):
                return [ValidationFailure([], "NumberOutOfRange", {})]
            else:
                return []
        else:
            return []
    else:
        return get_type_unexpected_validation_failure([], value, _NUMBER_NAME)
