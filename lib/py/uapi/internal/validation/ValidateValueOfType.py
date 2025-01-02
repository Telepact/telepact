from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_value_of_type(value: object, select: dict[str, object] | None, fn: str | None,
                           this_type: 'UType',
                           nullable: bool, type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if value is None:
        if not nullable:
            return get_type_unexpected_validation_failure([], value, this_type.get_name())
        else:
            return []

    return this_type.validate(value, select, fn, type_parameters)
