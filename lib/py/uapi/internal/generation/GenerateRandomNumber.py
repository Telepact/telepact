from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_number(ctx: 'GenerateContext') -> object:
    if ctx.use_blueprint_value:
        return ctx.blueprint_value
    else:
        return ctx.random_generator.next_double()
