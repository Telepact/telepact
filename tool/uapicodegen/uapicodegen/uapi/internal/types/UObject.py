from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.generation.GenerateContext import GenerateContext

from ...internal.types.UType import UType

_OBJECT_NAME: str = "Object"


class UObject(UType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateObject import validate_object
        return validate_object(value, type_parameters, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomObject import generate_random_object
        return generate_random_object(blueprint_value, use_blueprint_value, type_parameters, ctx)

    def get_name(self) -> str:
        return _OBJECT_NAME
