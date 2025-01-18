from typing import TYPE_CHECKING, cast
from uapi.internal.validation.ValidationFailure import ValidationFailure

if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_union_struct(
    union_struct: 'UStruct',
    union_case: str,
    actual: dict[str, object],
    selected_cases: dict[str, object],
    ctx: 'ValidateContext'
) -> list['ValidationFailure']:
    selected_fields = cast(list[str], selected_cases.get(
        union_case)) if selected_cases else None
    from uapi.internal.validation.ValidateStructFields import validate_struct_fields

    return validate_struct_fields(
        union_struct.fields,
        selected_fields,
        actual,
        ctx
    )
