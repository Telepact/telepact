from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_array(ctx: 'GenerateContext') -> list[object]:
    nested_type_declaration = ctx.type_parameters[0]

    if ctx.use_blueprint_value:
        starting_array = cast(list[object], ctx.blueprint_value)

        array = []
        for starting_array_value in starting_array:
            value = nested_type_declaration.generate_random_value(
                ctx.copy(blueprint_value=starting_array_value))

            array.append(value)

        return array
    else:
        length = ctx.random_generator.next_collection_length()

        array = []
        for i in range(length):
            value = nested_type_declaration.generate_random_value(ctx)

            array.append(value)

        return array
