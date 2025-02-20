from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext

from ...internal.types.UType import UType

_INTEGER_NAME: str = "Integer"


class UInteger(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateInteger import validate_integer
        return validate_integer(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomInteger import generate_random_integer
        return generate_random_integer(blueprint_value, use_blueprint_value, ctx)

    def get_name(self) -> str:
        return _INTEGER_NAME
