from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_fn(blueprint_value: object, use_blueprint_value: bool, call_cases: dict[str, 'UStruct'], ctx: 'GenerateContext') -> object:
    from uapi.internal.generation.GenerateRandomUnion import generate_random_union

    return generate_random_union(blueprint_value, use_blueprint_value, call_cases, ctx)
