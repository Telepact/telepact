from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.generation.GenerateContext import GenerateContext
    from uapi.RandomGenerator import RandomGenerator


def generate_random_any(ctx: 'GenerateContext') -> object:
    select_type = ctx.random_generator.next_int_with_ceiling(3)
    if select_type == 0:
        return ctx.random_generator.next_boolean()
    elif select_type == 1:
        return ctx.random_generator.next_int()
    else:
        return ctx.random_generator.next_string()
