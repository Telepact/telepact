from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.validation.ValidationFailure import ValidationFailure


def map_validation_failures_to_invalid_field_cases(
        argument_validation_failures: list['ValidationFailure']) -> list[dict[str, object]]:
    validation_failure_cases: list[dict[str, object]] = []
    for validation_failure in argument_validation_failures:
        validation_failure_case: dict[str, object] = {
            "path": validation_failure.path,
            "reason": {validation_failure.reason: validation_failure.data}
        }
        validation_failure_cases.append(validation_failure_case)

    return validation_failure_cases
