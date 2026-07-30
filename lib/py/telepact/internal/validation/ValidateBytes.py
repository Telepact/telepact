#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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
        if ctx.coerce_base64:
            set_coerced_path(ctx.path, ctx.base64_coercions)
        return []
    if isinstance(value, str):
        try:
            base64.b64decode(value)
            if not ctx.coerce_base64:
                set_coerced_path(ctx.path, ctx.bytes_coercions)
            return []
        except Exception as e:
            return get_type_unexpected_validation_failure([], value, 'Base64String')
    else:
        return get_type_unexpected_validation_failure([], value, _BYTES_NAME)
        

def set_coerced_path(path: list[str], coerced_path: dict[str, object]):
    part = path[0]

    if len(path) > 1:
        coerced_path[part] = coerced_path.get(part, {})
        set_coerced_path(path[1:], cast(dict[str, object], coerced_path[part]))
    else:
        coerced_path[part] = True
