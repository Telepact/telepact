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

from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ..types.TStruct import TStruct
    from ..types.TTypeDeclaration import TTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_fn(blueprint_value: object, use_blueprint_value: bool, call_tags: dict[str, 'TStruct'], ctx: 'GenerateContext') -> object:
    from ...internal.generation.GenerateRandomUnion import generate_random_union

    return generate_random_union(blueprint_value, use_blueprint_value, call_tags, ctx)
