from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_struct(blueprint_value: object, use_blueprint_value: bool,
                           reference_struct: dict[str, 'UFieldDeclaration'], ctx: 'GenerateContext') -> object:
    sorted_reference_struct = sorted(
        reference_struct.items(), key=lambda x: x[0])

    starting_struct = cast(
        dict[str, object], blueprint_value) if use_blueprint_value else {}

    obj = {}
    for field_name, field_declaration in sorted_reference_struct:
        this_use_blueprint_value = field_name in starting_struct
        type_declaration = field_declaration.type_declaration

        if this_use_blueprint_value:
            this_blueprint_value = starting_struct.get(field_name)
            value = type_declaration.generate_random_value(
                this_blueprint_value, this_use_blueprint_value, ctx)
        else:
            if not field_declaration.optional:
                value = type_declaration.generate_random_value(
                    None, False, ctx)
            else:
                if not ctx.include_optional_fields or (ctx.randomize_optional_fields and ctx.random_generator.next_boolean()):
                    continue
                value = type_declaration.generate_random_value(
                    None, False, ctx)

        obj[field_name] = value

    return obj
