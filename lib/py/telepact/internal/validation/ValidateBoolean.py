#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
from ..types.TBoolean import _BOOLEAN_NAME
from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

if TYPE_CHECKING:
    from ...internal.validation.ValidationFailure import ValidationFailure


def validate_boolean(value: object) -> list['ValidationFailure']:
    if type(value) is bool:
        return []
    if isinstance(value, bool):
        return []
    return get_type_unexpected_validation_failure([], value, _BOOLEAN_NAME)
