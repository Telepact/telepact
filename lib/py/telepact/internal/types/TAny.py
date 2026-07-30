#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .TTypeDeclaration import TTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .TType import TType

_ANY_NAME = "Any"


class TAny(TType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        return []

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomAny import generate_random_any
        return generate_random_any(ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _ANY_NAME
