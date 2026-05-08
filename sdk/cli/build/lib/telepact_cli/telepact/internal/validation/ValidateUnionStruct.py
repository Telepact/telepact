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
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.TStruct import TStruct
    from ..types.TTypeDeclaration import TTypeDeclaration


def validate_union_struct(
    union_struct: 'TStruct',
    union_tag: str,
    actual: dict[str, object],
    selected_tags: dict[str, object],
    ctx: 'ValidateContext'
) -> list['ValidationFailure']:
    selected_fields = cast(list[str], selected_tags.get(
        union_tag)) if selected_tags else None
    from ...internal.validation.ValidateStructFields import validate_struct_fields

    ctx.path.append(union_tag)

    result = validate_struct_fields(
        union_struct.fields,
        selected_fields,
        actual,
        ctx
    )

    ctx.path.pop()

    return result
