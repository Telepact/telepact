#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
from ...TelepactError import TelepactError

if TYPE_CHECKING:
    from ..types.TUnion import TUnion


def validate_result(result_union_type: 'TUnion', error_result: object) -> None:
    from ...internal.validation.MapValidationFailuresToInvalidFieldCases import map_validation_failures_to_invalid_field_cases
    from ...internal.validation.ValidateContext import ValidateContext

    new_error_result_validation_failures = result_union_type.validate(
        error_result, [], ValidateContext(None, None)
    )
    if new_error_result_validation_failures:
        raise TelepactError(
            f"Failed internal telepact validation: {map_validation_failures_to_invalid_field_cases(new_error_result_validation_failures)}"
        )
