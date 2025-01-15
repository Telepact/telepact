from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_value_of_type(ctx: 'GenerateContext',
                                  this_type: 'UType', nullable: bool,
                                  type_parameters: list['UTypeDeclaration']) -> object:
    if nullable and not ctx.use_blueprint_value and ctx.random_generator.next_boolean():
        return None
    else:
        return this_type.generate_random_value(ctx.copy(type_parameters=type_parameters))
