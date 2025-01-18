from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_STRING_NAME: str = "String"


class UString(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateString import validate_string
        return validate_string(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomString import generate_random_string
        return generate_random_string(blueprint_value, use_blueprint_value, ctx)

    def get_name(self) -> str:
        return _STRING_NAME
