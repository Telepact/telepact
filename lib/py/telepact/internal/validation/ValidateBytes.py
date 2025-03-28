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

from ...internal.types.TBytes import _BYTES_NAME

if TYPE_CHECKING:
    from .ValidationFailure import ValidationFailure
    from .ValidateContext import ValidateContext


def validate_bytes(value: object, ctx: 'ValidateContext') -> list['ValidationFailure']:
    from .GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if isinstance(value, bytes):
        print("Value is of type 'bytes'.")
        if ctx.coerce_base64:
            print("Coercion to base64 is enabled.")
            set_coerced_path(ctx.path, ctx.base64_coercions)
        return []
    if isinstance(value, str):
        print("Value is of type 'str'. Attempting base64 decoding.")
        try:
            base64.b64decode(value)
            print("Base64 decoding successful.")
            if not ctx.coerce_base64:
                print("Coercion to bytes is enabled.")
                set_coerced_path(ctx.path, ctx.bytes_coercions)
            return []
        except Exception as e:
            print(f"Base64 decoding failed: {e}")
            return get_type_unexpected_validation_failure([], value, 'Base64String')
    else:
        print(f"Value is of unexpected type: {type(value)}")
        return get_type_unexpected_validation_failure([], value, _BYTES_NAME)
        

def set_coerced_path(path: list[str], coerced_path: dict[str, object]):
    print(f'Setting coerced path: {path}')
    part = path[0]
    print(f'Current part: {part}')

    if len(path) > 1:
        print(f'Path has more parts: {path[1:]}')
        coerced_path[part] = coerced_path.get(part, {})
        set_coerced_path(path[1:], cast(dict[str, object], coerced_path[part]))
    else:
        print(f'Final part reached. Setting {part} to True.')
        coerced_path[part] = True
