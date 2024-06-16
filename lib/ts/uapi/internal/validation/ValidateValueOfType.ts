from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def validate_value_of_type(value: object, select: dict[str, object] | None, fn: str | None,
                           generics: list['UTypeDeclaration'], this_type: 'UType',
                           nullable: bool, type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
    from uapi.internal.validation.GetTypeUnexpectedValidationFailure import get_type_unexpected_validation_failure
    from uapi.internal.types.UGeneric import UGeneric

    if value is None:
        is_nullable = nullable
        if isinstance(this_type, UGeneric):
            generic_index = this_type.index
            generic = generics[generic_index]
            is_nullable = generic.nullable

        if not is_nullable:
            return get_type_unexpected_validation_failure([], value, this_type.get_name(generics))
        else:
            return []

    return this_type.validate(value, select, fn, type_parameters, generics)
