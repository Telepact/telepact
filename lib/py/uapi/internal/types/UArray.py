from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


from uapi.internal.types.UType import UType

_ARRAY_NAME = "Array"


class UArray(UType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateArray import validate_array
        return validate_array(value, select, fn, type_parameters, generics)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomArray import generate_random_array
        return generate_random_array(blueprint_value, use_blueprint_value, include_optional_fields,
                                     randomize_optional_fields, type_parameters, generics, random_generator)

    def get_name(self, generics: list['UTypeDeclaration']) -> str:
        return _ARRAY_NAME
