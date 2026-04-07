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
    from ..types.TTypeDeclaration import TTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_array(blueprint_value: object, use_blueprint_value: bool, type_parameters: list['TTypeDeclaration'], ctx: 'GenerateContext') -> list[object]:
    nested_type_declaration = type_parameters[0]

    if use_blueprint_value:
        starting_array = cast(list[object], blueprint_value)

        array = []
        for starting_array_value in starting_array:
            value = nested_type_declaration.generate_random_value(
                starting_array_value, True, ctx)

            array.append(value)

        return array
    else:
        length = ctx.random_generator.next_collection_length()

        array = []
        for i in range(length):
            value = nested_type_declaration.generate_random_value(
                None, False, ctx)

            array.append(value)

        return array
