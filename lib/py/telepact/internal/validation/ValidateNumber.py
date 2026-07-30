#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from ..types.TNumber import _NUMBER_NAME
from ...internal.validation.ValidationFailure import ValidationFailure
from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
from ...internal.validation.Int64Bounds import MIN_INT64, MAX_INT64


def _validate_integer_number(value: int) -> list['ValidationFailure']:
    if value > MAX_INT64 or value < MIN_INT64:
        return [ValidationFailure([], "NumberOutOfRange", {})]
    return []


def validate_number(value: object) -> list['ValidationFailure']:
    value_type = type(value)
    if value_type is int:
        return _validate_integer_number(value)
    if value_type is float:
        return []
    if isinstance(value, int) and not isinstance(value, (bool, str)):
        return _validate_integer_number(value)
    if isinstance(value, float) and not isinstance(value, str):
        return []
    return get_type_unexpected_validation_failure([], value, _NUMBER_NAME)
