#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING
from ...Message import Message

if TYPE_CHECKING:
    from ..types.TUnion import TUnion
    from ...internal.validation.ValidationFailure import ValidationFailure


def get_invalid_error_message(error: str, validation_failures: list['ValidationFailure'],
                              result_union_type: 'TUnion', response_headers: dict[str, object]) -> 'Message':
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
