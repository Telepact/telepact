from typing import List
from uapi.internal.validation.MapValidationFailuresToInvalidFieldCases import mapValidationFailuresToInvalidFieldCases
from uapi.UApiError import UApiError
from uapi.internal.types.UUnion import UUnion


def validate_result(result_union_type: UUnion, error_result: object) -> None:
    new_error_result_validation_failures = result_union_type.validate(
        error_result, None, None, [], []
    )
    if new_error_result_validation_failures:
        raise UApiError(
            f"Failed internal uAPI validation: {mapValidationFailuresToInvalidFieldCases(new_error_result_validation_failures)}"
        )
