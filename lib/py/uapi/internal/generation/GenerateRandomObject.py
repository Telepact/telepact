from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_object(ctx: 'GenerateContext') -> object:
    nested_type_declaration = ctx.type_parameters[0]

    if ctx.use_blueprint_value:
        starting_obj = cast(dict[str, object], ctx.blueprint_value)

        obj = {}
        for key, starting_obj_value in starting_obj.items():
            value = nested_type_declaration.generate_random_value(
                ctx.copy(blueprint_value=starting_obj_value))
            obj[key] = value

        return obj
    else:
        length = ctx.random_generator.next_collection_length()

        obj = {}
        for i in range(length):
            key = ctx.random_generator.next_string()
            value = nested_type_declaration.generate_random_value(ctx)
            obj[key] = value

        return obj
