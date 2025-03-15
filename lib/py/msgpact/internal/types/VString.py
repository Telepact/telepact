from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .VTypeDeclaration import VTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .VType import VType

_STRING_NAME: str = "String"


class VString(VType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateString import validate_string
        return validate_string(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomString import generate_random_string
        return generate_random_string(blueprint_value, use_blueprint_value, ctx)

    def get_name(self) -> str:
        return _STRING_NAME
