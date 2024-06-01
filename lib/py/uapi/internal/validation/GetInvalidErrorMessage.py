from typing import List, Dict, Any
from uapi import Message
from uapi.internal.types import UUnion

from uapi.internal.validation import (
    map_validation_failures_to_invalid_field_cases,
    validate_result
)


def get_invalid_error_message(error: str, validation_failures: List[ValidationFailure],
                              result_union_type: UUnion, response_headers: Dict[str, Any]) -> Message:
    validation_failure_cases = map_validation_failures_to_invalid_field_cases(
        validation_failures)
    new_error_result = {
        error: {
            "cases": validation_failure_cases
        }
    }

    validate_result(result_union_type, new_error_result)
    return Message(response_headers, new_error_result)
