from typing import TYPE_CHECKING
from ...Message import Message

if TYPE_CHECKING:
    from ...internal.types.UUnion import UUnion
    from ...internal.validation.ValidationFailure import ValidationFailure


def get_invalid_error_message(error: str, validation_failures: list['ValidationFailure'],
                              result_union_type: 'UUnion', response_headers: dict[str, object]) -> 'Message':
    from ...internal.validation.MapValidationFailuresToInvalidFieldCases import map_validation_failures_to_invalid_field_cases
    from ...internal.validation.ValidateResult import validate_result

    validation_failure_cases = map_validation_failures_to_invalid_field_cases(
        validation_failures)
    new_error_result: dict[str, object] = {
        error: {
            "cases": validation_failure_cases
        }
    }

    validate_result(result_union_type, new_error_result)
    return Message(response_headers, new_error_result)
