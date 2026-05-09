#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from ..types.TString import _STRING_NAME
from ...internal.validation.ValidationFailure import ValidationFailure


def validate_string(value: object) -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, str):
        return []
    else:
        return get_type_unexpected_validation_failure([], value, _STRING_NAME)
