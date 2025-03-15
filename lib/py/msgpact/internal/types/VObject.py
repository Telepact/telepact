from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .VTypeDeclaration import VTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .VType import VType

_OBJECT_NAME: str = "Object"


class VObject(VType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateObject import validate_object
        return validate_object(value, type_parameters, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomObject import generate_random_object
        return generate_random_object(blueprint_value, use_blueprint_value, type_parameters, ctx)

    def get_name(self) -> str:
        return _OBJECT_NAME
