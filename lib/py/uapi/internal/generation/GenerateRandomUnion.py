from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_union(blueprint_value: object, use_blueprint_value: bool,
                          union_tags_reference: dict[str, 'UStruct'], ctx: 'GenerateContext') -> object:
    from uapi.internal.generation.GenerateRandomStruct import generate_random_struct

    if not use_blueprint_value:
        sorted_union_tags_reference = sorted(
            union_tags_reference.items(), key=lambda x: x[0])
        random_index = ctx.random_generator.next_int_with_ceiling(
            len(sorted_union_tags_reference) - 1)
        union_tag, union_data = sorted_union_tags_reference[random_index]
        return {union_tag: generate_random_struct(None, False, union_data.fields, ctx)}
    else:
        starting_union = cast(dict[str, object], blueprint_value)
        union_tag, union_starting_struct = cast(
            tuple[str, dict[str, object]], next(iter(starting_union.items())))
        union_struct_type = union_tags_reference[union_tag]
        return {union_tag: generate_random_struct(union_starting_struct, True, union_struct_type.fields, ctx)}
