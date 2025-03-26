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

from typing import TYPE_CHECKING, cast
import base64

if TYPE_CHECKING:
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.validation.ValidateContext import ValidateContext


def validate_binary(value: object, ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    expected_type = 'Bytes' if ctx.binary else 'Base64String'

    if ctx.coerce_base64:
        if isinstance(value, str):
            return []
        elif isinstance(value, bytes):
            new_b64_value: str = base64.b64encode(value).decode("utf-8")
            ctx.new_value = new_b64_value

            set_coerced_path(ctx.path, ctx.coercions)

            return []
        else:
            return get_type_unexpected_validation_failure([], value, expected_type)
    else:
        if isinstance(value, bytes):
            return []
        elif isinstance(value, str):
            try:
                new_bytes_value: bytes = base64.b64decode(value)
                ctx.new_value = new_bytes_value
                return []
            except Exception:
                return get_type_unexpected_validation_failure([], value, expected_type)
        else:
            return get_type_unexpected_validation_failure([], value, expected_type)
        

def set_coerced_path(path: list[str], coerced_path: dict[str, object]):
    part = path[0]

    if len(path) > 1:
        coerced_path[part] = coerced_path.get(part, {})
        set_coerced_path(path[1:], cast(dict[str, object], coerced_path[part]))
    else:
        coerced_path[part] = True
