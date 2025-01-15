from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_INTEGER_NAME: str = "Integer"


class UInteger(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateInteger import validate_integer
        return validate_integer(value)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomInteger import generate_random_integer
        return generate_random_integer(ctx)

    def get_name(self) -> str:
        return _INTEGER_NAME
