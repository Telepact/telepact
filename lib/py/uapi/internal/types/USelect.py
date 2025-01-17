from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_SELECT: str = "Object"


class USelect(UType):

    possible_selects: dict[str, object] = {}

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateSelect import validate_select
        return validate_select(given_obj, cast(str, fn), self.possible_selects)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomSelect import generate_random_select
        return generate_random_select(self.possible_selects, ctx)

    def get_name(self) -> str:
        return _SELECT
