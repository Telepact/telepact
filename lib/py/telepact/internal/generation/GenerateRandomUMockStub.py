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

from ...internal.generation.GenerateContext import GenerateContext
from ...internal.generation.GenerateRandomStruct import generate_random_struct
from ..types.VFn import VFn
from ..types.VType import VType


def generate_random_u_mock_stub(types: dict[str, VType], ctx: GenerateContext) -> object:
    functions = [value for key, value in types.items() if isinstance(
        value, VFn) and not key.endswith('_')]

    functions.sort(key=lambda fn: fn.name)

    print(f"randomSeed: {ctx.random_generator.seed}")
    print(f"functions: {[fn.name for fn in functions]}")

    index = ctx.random_generator.next_int_with_ceiling(len(functions))

    print(f"index: {index}")

    selected_fn = functions[index]

    print(f"selectedFn: {selected_fn.name}")

    arg_fields = selected_fn.call.tags[selected_fn.name].fields
    ok_fields = selected_fn.result.tags['Ok_'].fields

    arg = generate_random_struct(None, False, arg_fields, ctx.copy(
        always_include_required_fields=False))
    ok_result = generate_random_struct(None, False,
                                       ok_fields, ctx.copy(always_include_required_fields=False))

    return {
        selected_fn.name: arg,
        '->': {
            'Ok_': ok_result,
        },
    }
