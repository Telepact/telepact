#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

from ..validation.ValidateValueOfType import validate_value_of_type

if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .TType import TType
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext


class TTypeDeclaration:
    def __init__(self, type: 'TType', nullable: bool, type_parameters: list['TTypeDeclaration']):
        self.type = type
        self.nullable = nullable
        self.type_parameters = type_parameters

    def validate(self, value: object, ctx: 'ValidateContext') -> list['ValidationFailure']:
        return validate_value_of_type(value, self.type, self.nullable, self.type_parameters, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomValueOfType import generate_random_value_of_type
        return generate_random_value_of_type(blueprint_value, use_blueprint_value, self.type, self.nullable, self.type_parameters, ctx)
