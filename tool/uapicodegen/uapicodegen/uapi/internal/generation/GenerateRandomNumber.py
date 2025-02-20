from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_number(blueprint_value: object, use_blueprint_value: bool, ctx: 'GenerateContext') -> object:
    if use_blueprint_value:
        return blueprint_value
    else:
        return ctx.random_generator.next_double()
