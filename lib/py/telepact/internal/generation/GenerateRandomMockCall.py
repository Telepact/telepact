#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import cast

from .GenerateContext import GenerateContext
from .GenerateRandomUnion import generate_random_union
from ..types.TType import TType


def generate_random_mock_call(types: dict[str, TType], ctx: GenerateContext) -> object:
    from ..types.TUnion import TUnion

    function_names = [
        key for key in types.keys()
        if key.startswith('fn.') and not key.endswith('.->') and not key.endswith('_')
    ]

    function_names.sort()

    selected_fn_name = function_names[ctx.random_generator.next_int_with_ceiling(
        len(function_names))]
    
    selected_fn = cast(TUnion, types[selected_fn_name])

    return generate_random_union(None, False, selected_fn.tags, ctx.copy(always_include_required_fields=False))
