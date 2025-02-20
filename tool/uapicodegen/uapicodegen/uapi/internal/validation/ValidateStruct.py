from typing import TYPE_CHECKING, cast
from ...internal.types.UStruct import _STRUCT_NAME

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.types.UFieldDeclaration import UFieldDeclaration
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.validation.ValidationFailure import ValidationFailure


def validate_struct(value: object,
                    name: str, fields: dict[str, 'UFieldDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from ...internal.validation.ValidateStructFields import validate_struct_fields

    if isinstance(value, dict):
        selected_fields = cast(
            list[str], ctx.select.get(name) if ctx.select else None)
        return validate_struct_fields(fields, selected_fields, value, ctx)
    else:
        return get_type_unexpected_validation_failure([], value, _STRUCT_NAME)
