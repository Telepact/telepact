#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ..validation.ValidationFailure import ValidationFailure
    from .TTypeDeclaration import TTypeDeclaration
    from ..generation.GenerateContext import GenerateContext

from .TType import TType

_INTEGER_NAME: str = "Integer"


class TInteger(TType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateInteger import validate_integer
        return validate_integer(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomInteger import generate_random_integer
        return generate_random_integer(blueprint_value, use_blueprint_value, ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _INTEGER_NAME
