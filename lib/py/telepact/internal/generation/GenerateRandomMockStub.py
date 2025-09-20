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

from .GenerateContext import GenerateContext
from .GenerateRandomStruct import generate_random_struct
from ..types.TType import TType


def generate_random_mock_stub(types: dict[str, TType], ctx: GenerateContext) -> object:
    from ..types.TUnion import TUnion

    functions = [key for key in types.keys() if key.startswith('fn.') and not key.endswith('.->') and not key.endswith('_')]

    functions.sort()

    index = ctx.random_generator.next_int_with_ceiling(len(functions))

    selected_fn_name = functions[index]
    selected_fn = cast(TUnion, types[selected_fn_name])
    selected_result = cast(TUnion, types[selected_fn_name + '.->'])

    arg_fields = selected_fn.tags[selected_fn_name].fields
    ok_fields = selected_result.tags['Ok_'].fields

    arg = generate_random_struct(None, False, arg_fields, ctx.copy(
        always_include_required_fields=False))
    ok_result = generate_random_struct(None, False,
                                       ok_fields, ctx.copy(always_include_required_fields=False))

    return {
        selected_fn_name: arg,
        '->': {
            'Ok_': ok_result,
        },
    }
