from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.generation.GenerateContext import GenerateContext


from ...internal.types.UType import UType

_NUMBER_NAME: str = "Number"


class UNumber(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateNumber import validate_number
        return validate_number(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomNumber import generate_random_number
        return generate_random_number(blueprint_value, use_blueprint_value, ctx)

    def get_name(self) -> str:
        return _NUMBER_NAME
