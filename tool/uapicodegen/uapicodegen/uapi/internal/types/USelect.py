from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.generation.GenerateContext import GenerateContext

from ...internal.types.UType import UType

_SELECT: str = "Object"


class USelect(UType):

    possible_selects: dict[str, object] = {}

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateSelect import validate_select
        return validate_select(given_obj, self.possible_selects, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomSelect import generate_random_select
        return generate_random_select(self.possible_selects, ctx)

    def get_name(self) -> str:
        return _SELECT
