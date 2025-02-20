from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.types.UType import UType
    from ...internal.types.UTypeDeclaration import UTypeDeclaration


def validate_value_of_type(value: object,
                           this_type: 'UType',
                           nullable: bool, type_parameters: list['UTypeDeclaration'],
                           ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if value is None:
        if not nullable:
            return get_type_unexpected_validation_failure([], value, this_type.get_name())
        else:
            return []

    return this_type.validate(value, type_parameters, ctx)
