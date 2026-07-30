#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from ..types.TInteger import _INTEGER_NAME
from ...internal.validation.ValidationFailure import ValidationFailure
from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
from ...internal.validation.Int64Bounds import MIN_INT64, MAX_INT64


def validate_integer(value: object) -> list['ValidationFailure']:
    if type(value) is int:
        if value > MAX_INT64 or value < MIN_INT64:
            return [ValidationFailure([], "NumberOutOfRange", {})]
        return []
    if isinstance(value, int) and not isinstance(value, (bool, float)):
        if value > MAX_INT64 or value < MIN_INT64:
            return [ValidationFailure([], "NumberOutOfRange", {})]
        return []

    return get_type_unexpected_validation_failure([], value, _INTEGER_NAME)
