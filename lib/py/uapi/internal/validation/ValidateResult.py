from typing import List
from uapi.UApiError import UApiError
from uapi.internal.types.UUnion import UUnion
from uapi.internal.validation.MapValidationFailuresToInvalidFieldCases import map_validation_failures_to_invalid_field_cases


def validate_result(result_union_type: 'UUnion', error_result: object) -> None:
    new_error_result_validation_failures = result_union_type.validate(
        error_result, None, None, [], []
    )
    if new_error_result_validation_failures:
        raise UApiError(
            f"Failed internal uAPI validation: {map_validation_failures_to_invalid_field_cases(new_error_result_validation_failures)}"
        )
