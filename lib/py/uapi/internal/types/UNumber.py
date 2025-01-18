from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext


from uapi.internal.types.UType import UType

_NUMBER_NAME: str = "Number"


class UNumber(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateNumber import validate_number
        return validate_number(value)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomNumber import generate_random_number
        return generate_random_number(ctx)

    def get_name(self) -> str:
        return _NUMBER_NAME
