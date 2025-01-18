from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_BOOLEAN_NAME: str = "Boolean"


class UBoolean(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateBoolean import validate_boolean
        return validate_boolean(value)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomBoolean import generate_random_boolean
        return generate_random_boolean(ctx)

    def get_name(self) -> str:
        return _BOOLEAN_NAME
