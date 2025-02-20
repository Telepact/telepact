from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext

from ...internal.types.UType import UType

_BOOLEAN_NAME: str = "Boolean"


class UBoolean(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateBoolean import validate_boolean
        return validate_boolean(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomBoolean import generate_random_boolean
        return generate_random_boolean(blueprint_value, use_blueprint_value, ctx)

    def get_name(self) -> str:
        return _BOOLEAN_NAME
