from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_OBJECT_NAME: str = "Object"


class UObject(UType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateObject import validate_object
        return validate_object(value, type_parameters, ctx)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomObject import generate_random_object
        return generate_random_object(ctx)

    def get_name(self) -> str:
        return _OBJECT_NAME
