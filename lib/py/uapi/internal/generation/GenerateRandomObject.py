from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_object(blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
    nested_type_declaration = type_parameters[0]

    if use_blueprint_value:
        starting_obj = cast(dict[str, object], blueprint_value)

        obj = {}
        for key, starting_obj_value in starting_obj.items():
            value = nested_type_declaration.generate_random_value(
                starting_obj_value, True, ctx)
            obj[key] = value

        return obj
    else:
        length = ctx.random_generator.next_collection_length()

        obj = {}
        for i in range(length):
            key = ctx.random_generator.next_string()
            value = nested_type_declaration.generate_random_value(
                None, False, ctx)
            obj[key] = value

        return obj
