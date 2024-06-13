from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UType import UType
    from uapi.internal.validation.ValidationFailure import ValidationFailure


class UTypeDeclaration:
    def __init__(self, type: 'UType', nullable: bool, type_parameters: list['UTypeDeclaration']):
        self.type = type
        self.nullable = nullable
        self.type_parameters = type_parameters

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 generics: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateValueOfType import validate_value_of_type
        return validate_value_of_type(value, select, fn, generics, self.type, self.nullable, self.type_parameters)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              generics: list['UTypeDeclaration'], random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomValueOfType import generate_random_value_of_type
        return generate_random_value_of_type(blueprint_value, use_blueprint_value,
                                             include_optional_fields, randomize_optional_fields,
                                             generics, random_generator, self.type, self.nullable, self.type_parameters)
