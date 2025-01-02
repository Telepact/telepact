from typing import TYPE_CHECKING
from uapi.UApiError import UApiError

if TYPE_CHECKING:
    from uapi.internal.types.UUnion import UUnion


def validate_result(result_union_type: 'UUnion', error_result: object) -> None:
    from uapi.internal.validation.MapValidationFailuresToInvalidFieldCases import map_validation_failures_to_invalid_field_cases

    new_error_result_validation_failures = result_union_type.validate(
        error_result, None, None, []
    )
    if new_error_result_validation_failures:
        raise UApiError(
            f"Failed internal uAPI validation: {map_validation_failures_to_invalid_field_cases(new_error_result_validation_failures)}"
        )
