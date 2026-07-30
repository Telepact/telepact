#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING, cast
from ...internal.validation.ValidationFailure import ValidationFailure
from ...internal.validation.ValidateStructFields import validate_struct_fields

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

    ctx.path.append(union_tag)

    result = validate_struct_fields(
        union_struct.fields,
        selected_fields,
        actual,
        ctx
    )

    ctx.path.pop()

    return result
