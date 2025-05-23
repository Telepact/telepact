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

from typing import cast

from ...internal.generation.GenerateContext import GenerateContext
from ...internal.generation.GenerateRandomUnion import generate_random_union
from ..types.TType import TType


def generate_random_u_mock_call(types: dict[str, TType], ctx: GenerateContext) -> object:
    from ...internal.types.TUnion import TUnion

    function_names = [
        key for key in types.keys()
        if key.startswith('fn.') and not key.endswith('.->') and not key.endswith('_')
    ]

    function_names.sort()

    selected_fn_name = function_names[ctx.random_generator.next_int_with_ceiling(
        len(function_names))]
    
    selected_fn = cast(TUnion, types[selected_fn_name])

    return generate_random_union(None, False, selected_fn.tags, ctx.copy(always_include_required_fields=False))
