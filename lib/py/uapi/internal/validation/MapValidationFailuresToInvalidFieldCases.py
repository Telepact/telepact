from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.validation.ValidationFailure import ValidationFailure


def map_validation_failures_to_invalid_field_cases(
        argument_validation_failures: List['ValidationFailure']) -> List[Dict[str, Any]]:
    validation_failure_cases = []
    for validation_failure in argument_validation_failures:
        validation_failure_case = {
            "path": validation_failure.path,
            "reason": {validation_failure.reason: validation_failure.data}
        }
        validation_failure_cases.append(validation_failure_case)

    return validation_failure_cases
