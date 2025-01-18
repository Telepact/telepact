from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UType import UType
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext


class UTypeDeclaration:
    def __init__(self, type: 'UType', nullable: bool, type_parameters: list['UTypeDeclaration']):
        self.type = type
        self.nullable = nullable
        self.type_parameters = type_parameters

    def validate(self, value: object, ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateValueOfType import validate_value_of_type
        return validate_value_of_type(value, self.type, self.nullable, self.type_parameters, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomValueOfType import generate_random_value_of_type
        return generate_random_value_of_type(blueprint_value, use_blueprint_value, self.type, self.nullable, self.type_parameters, ctx)
