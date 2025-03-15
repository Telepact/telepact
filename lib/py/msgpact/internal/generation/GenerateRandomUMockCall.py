from ...internal.generation.GenerateContext import GenerateContext
from ...internal.generation.GenerateRandomUnion import generate_random_union
from ..types.VFn import VFn
from ..types.VType import VType


def generate_random_u_mock_call(types: dict[str, VType], ctx: GenerateContext) -> object:
    functions = [
        value for key, value in types.items()
        if isinstance(value, VFn) and not key.endswith('_')
    ]

    functions.sort(key=lambda fn: fn.name)

    selected_fn = functions[ctx.random_generator.next_int_with_ceiling(
        len(functions))]

    return generate_random_union(None, False, selected_fn.call.tags, ctx.copy(always_include_required_fields=False))
