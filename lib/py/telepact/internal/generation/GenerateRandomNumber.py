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
    from ...RandomGenerator import RandomGenerator
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_number(blueprint_value: object, use_blueprint_value: bool, ctx: 'GenerateContext') -> object:
    if use_blueprint_value:
        return blueprint_value
    else:
        return ctx.random_generator.next_double()
