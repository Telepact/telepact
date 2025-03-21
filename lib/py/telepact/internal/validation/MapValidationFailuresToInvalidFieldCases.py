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

if TYPE_CHECKING:
    from ...internal.validation.ValidationFailure import ValidationFailure


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
