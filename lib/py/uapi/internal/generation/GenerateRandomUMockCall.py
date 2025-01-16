from uapi.internal.generation.GenerateContext import GenerateContext
from uapi.internal.generation.GenerateRandomUnion import generate_random_union
from uapi.internal.types.UFn import UFn
from uapi.internal.types.UType import UType


def generate_random_u_mock_call(types: dict[str, UType], ctx: GenerateContext) -> object:
    functions = [
        value for key, value in types.items()
        if isinstance(value, UFn) and not key.endswith('_')
    ]

    functions.sort(key=lambda fn: fn.name)

    selected_fn = functions[ctx.random_generator.next_int_with_ceiling(
        len(functions))]

    return generate_random_union(selected_fn.call.cases, ctx.copy(always_include_required_fields=False))
