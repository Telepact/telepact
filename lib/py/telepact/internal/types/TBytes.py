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

_BYTES_NAME: str = "Bytes"

class TBytes(TType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateBytes import validate_bytes
        return validate_bytes(value, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomBytes import generate_random_bytes
        return generate_random_bytes(blueprint_value, use_blueprint_value, ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _BYTES_NAME
