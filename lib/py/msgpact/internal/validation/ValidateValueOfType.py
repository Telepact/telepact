from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ..types.VType import VType
    from ..types.VTypeDeclaration import VTypeDeclaration


def validate_value_of_type(value: object,
                           this_type: 'VType',
                           nullable: bool, type_parameters: list['VTypeDeclaration'],
                           ctx: 'ValidateContext') -> list['ValidationFailure']:
    from ...internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure

    if value is None:
        if not nullable:
            return get_type_unexpected_validation_failure([], value, this_type.get_name())
        else:
            return []

    return this_type.validate(value, type_parameters, ctx)
