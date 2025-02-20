from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ...internal.types.UStruct import UStruct
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_fn(blueprint_value: object, use_blueprint_value: bool, call_tags: dict[str, 'UStruct'], ctx: 'GenerateContext') -> object:
    from ...internal.generation.GenerateRandomUnion import generate_random_union

    return generate_random_union(blueprint_value, use_blueprint_value, call_tags, ctx)
