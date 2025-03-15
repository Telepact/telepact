from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .VTypeDeclaration import VTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext


from .VType import VType

_NUMBER_NAME: str = "Number"


class VNumber(VType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateNumber import validate_number
        return validate_number(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomNumber import generate_random_number
        return generate_random_number(blueprint_value, use_blueprint_value, ctx)

    def get_name(self) -> str:
        return _NUMBER_NAME
