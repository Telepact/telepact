from typing import TYPE_CHECKING, cast
from uapi.internal.types.UStruct import _STRUCT_NAME

if TYPE_CHECKING:
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure


def validate_struct(value: object, select: dict[str, object] | None, fn: str | None,
                    type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration'],
                    name: str, fields: dict[str, 'UFieldDeclaration']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.validation.ValidateStructFields import validate_struct_fields

    if isinstance(value, dict):
        selected_fields = cast(
            list[str], select.get(name) if select else None)
        return validate_struct_fields(fields, selected_fields, value, select, fn, type_parameters)
    else:
        return get_type_unexpected_validation_failure([], value, _STRUCT_NAME)
