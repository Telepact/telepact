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
from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
from ...internal.validation.Int64Bounds import MIN_INT64, MAX_INT64


def validate_integer(value: object) -> list['ValidationFailure']:
    if type(value) is int:
        if value > MAX_INT64 or value < MIN_INT64:
            return [ValidationFailure([], "NumberOutOfRange", {})]
        return []
    if isinstance(value, int) and not isinstance(value, (bool, float)):
        if value > MAX_INT64 or value < MIN_INT64:
            return [ValidationFailure([], "NumberOutOfRange", {})]
        return []

    return get_type_unexpected_validation_failure([], value, _INTEGER_NAME)
