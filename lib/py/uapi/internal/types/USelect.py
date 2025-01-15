from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_SELECT: str = "Object"


class USelect(UType):

    def __init__(self, types: dict[str, 'UType']) -> None:
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateSelect import validate_select
        return validate_select(given_obj, select, fn, type_parameters, self.types)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        raise NotImplementedError("Not implemented")

    def get_name(self) -> str:
        return _SELECT
