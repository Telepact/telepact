from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ..types.VType import VType
    from ..types.VTypeDeclaration import VTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_value_of_type(
        blueprint_value: object, use_blueprint_value: bool,
        this_type: 'VType', nullable: bool,
        type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
    if nullable and not use_blueprint_value and ctx.random_generator.next_boolean():
        return None
    else:
        return this_type.generate_random_value(blueprint_value, use_blueprint_value, type_parameters, ctx)
