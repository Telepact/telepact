from typing import List, Union
from decimal import Decimal
from numbers import Integral
from uapi.internal.types import UInteger
from uapi.internal.validation import GetTypeUnexpectedValidationFailure, ValidationFailure


def validate_integer(value: Union[int, Integral, Decimal]) -> List[ValidationFailure]:
    if isinstance(value, (int, Integral)):
        return []
    elif isinstance(value, (int, Decimal)):
        return [
            ValidationFailure([], "NumberOutOfRange", {})
        ]
    else:
        return GetTypeUnexpectedValidationFailure([], value, UInteger._INTEGER_NAME)
