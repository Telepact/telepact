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

_BOOLEAN_NAME: str = "Boolean"


class TBoolean(TType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateBoolean import validate_boolean
        return validate_boolean(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomBoolean import generate_random_boolean
        return generate_random_boolean(blueprint_value, use_blueprint_value, ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _BOOLEAN_NAME
