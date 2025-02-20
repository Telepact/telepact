from typing import TYPE_CHECKING, cast
from ...internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.types.UStruct import UStruct
    from ...internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union_struct(
    union_struct: 'UStruct',
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
