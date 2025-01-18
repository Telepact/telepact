from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_value_of_type(
        blueprint_value: object, use_blueprint_value: bool,
        this_type: 'UType', nullable: bool,
        type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
    if nullable and not use_blueprint_value and ctx.random_generator.next_boolean():
        return None
    else:
        return this_type.generate_random_value(blueprint_value, use_blueprint_value, type_parameters, ctx)
