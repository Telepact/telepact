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
from .TType import TType

if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ..generation.GenerateContext import GenerateContext
    from ...RandomGenerator import RandomGenerator
    from ..validation.ValidationFailure import ValidationFailure
    from .TStruct import TStruct
    from .TTypeDeclaration import TTypeDeclaration

_UNION_NAME: str = "Object"


class TUnion(TType):

    def __init__(self, name: str, tags: dict[str, 'TStruct'], tag_indices: dict[str, int]) -> None:
        self.name = name
        self.tags = tags
        self.tag_indices = tag_indices

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: list['TTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateUnion import validate_union
        return validate_union(value, self.name, self.tags, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomUnion import generate_random_union
        return generate_random_union(blueprint_value, use_blueprint_value, self.tags, ctx)

    def get_name(self, ctx: 'ValidateContext') -> str:
        return _UNION_NAME
