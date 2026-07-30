#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .TTypeDeclaration import TTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .TType import TType

_SELECT: str = "Object"


class TSelect(TType):

    possible_selects: dict[str, object] = {}

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object,
                 type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateSelect import validate_select
        return validate_select(given_obj, self.possible_selects, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomSelect import generate_random_select
        return generate_random_select(self.possible_selects, ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _SELECT
