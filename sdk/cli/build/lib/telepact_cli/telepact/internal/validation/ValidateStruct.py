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
from ..types.TStruct import _STRUCT_NAME

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TFieldDeclaration import TFieldDeclaration
    from ..types.TTypeDeclaration import TTypeDeclaration
    from ...internal.validation.ValidationFailure import ValidationFailure


def validate_struct(value: object,
                    name: str, fields: dict[str, 'TFieldDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ...internal.validation.ValidateStructFields import validate_struct_fields

    if isinstance(value, dict):
        selected_fields = cast(
            list[str], ctx.select.get(name) if ctx.select else None)
        return validate_struct_fields(fields, selected_fields, value, ctx)
    else:
        return get_type_unexpected_validation_failure([], value, _STRUCT_NAME)
