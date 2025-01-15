from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_struct(
        reference_struct: dict[str, 'UFieldDeclaration'], ctx: 'GenerateContext') -> object:
    sorted_reference_struct = sorted(
        reference_struct.items(), key=lambda x: x[0])

    starting_struct = cast(
        dict[str, object], ctx.blueprint_value) if ctx.use_blueprint_value else {}

    obj = {}
    for field_name, field_declaration in sorted_reference_struct:
        blueprint_value = starting_struct.get(field_name)
        use_blueprint_value = field_name in starting_struct
        type_declaration = field_declaration.type_declaration

        if use_blueprint_value:
            value = type_declaration.generate_random_value(ctx.copy(
                blueprint_value=blueprint_value, use_blueprint_value=use_blueprint_value))
        else:
            if not field_declaration.optional:
                value = type_declaration.generate_random_value(ctx)
            else:
                if not ctx.include_optional_fields or (ctx.randomize_optional_fields and ctx.random_generator.next_boolean()):
                    continue
                value = type_declaration.generate_random_value(ctx)

        obj[field_name] = value

    return obj
