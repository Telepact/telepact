from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ...RandomGenerator import RandomGenerator
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext


def generate_random_array(blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> list[object]:
    nested_type_declaration = type_parameters[0]

    if use_blueprint_value:
        starting_array = cast(list[object], blueprint_value)

        array = []
        for starting_array_value in starting_array:
            value = nested_type_declaration.generate_random_value(
                starting_array_value, True, ctx)

            array.append(value)

        return array
    else:
        length = ctx.random_generator.next_collection_length()

        array = []
        for i in range(length):
            value = nested_type_declaration.generate_random_value(
                None, False, ctx)

            array.append(value)

        return array
