#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .TTypeDeclaration import TTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .TType import TType

_OBJECT_NAME: str = "Object"


class TObject(TType):

    def get_type_parameter_count(self) -> int:
        return 1

    def validate(self, value: object,
                 type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateObject import validate_object
        return validate_object(value, type_parameters, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomObject import generate_random_object
        return generate_random_object(blueprint_value, use_blueprint_value, type_parameters, ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _OBJECT_NAME
