from typing import TYPE_CHECKING, cast
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ..types.VStruct import VStruct
    from ..types.VTypeDeclaration import VTypeDeclaration


def validate_union_struct(
    union_struct: 'VStruct',
    union_tag: str,
    actual: dict[str, object],
    selected_tags: dict[str, object],
    ctx: 'ValidateContext'
) -> list['ValidationFailure']:
    selected_fields = cast(list[str], selected_tags.get(
        union_tag)) if selected_tags else None
    from ...internal.validation.ValidateStructFields import validate_struct_fields

    return validate_struct_fields(
        union_struct.fields,
        selected_fields,
        actual,
        ctx
    )
