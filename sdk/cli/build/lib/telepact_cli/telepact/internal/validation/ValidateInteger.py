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

from ..types.TInteger import _INTEGER_NAME
from ...internal.validation.ValidationFailure import ValidationFailure


def validate_integer(value: object) -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, (int)) and not isinstance(value, (bool, float)):
        if (value > 2**63-1 or value < -(2**63)):
            return [ValidationFailure([], "NumberOutOfRange", {})]
        else:
            return []

    return get_type_unexpected_validation_failure([], value, _INTEGER_NAME)
