from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


from uapi.internal.types.UType import UType

_ARRAY_NAME = "Array"


class UArray(UType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateArray import validate_array
        return validate_array(value, select, fn, type_parameters)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomArray import generate_random_array
        return generate_random_array(ctx)

    def get_name(self) -> str:
        return _ARRAY_NAME
