from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext


def generate_random_union(
        union_cases_reference: dict[str, 'UStruct'], ctx: 'GenerateContext') -> object:
    from uapi.internal.generation.GenerateRandomStruct import generate_random_struct

    if not ctx.use_blueprint_value:
        sorted_union_cases_reference = sorted(
            union_cases_reference.items(), key=lambda x: x[0])
        random_index = ctx.random_generator.next_int_with_ceiling(
            len(sorted_union_cases_reference) - 1)
        union_case, union_data = sorted_union_cases_reference[random_index]
        return {union_case: generate_random_struct(union_data.fields, ctx)}
    else:
        starting_union = cast(dict[str, object], ctx.blueprint_value)
        union_case, union_starting_struct = cast(
            tuple[str, dict[str, object]], next(iter(starting_union.items())))
        union_struct_type = union_cases_reference[union_case]
        return {union_case: generate_random_struct(union_struct_type.fields, ctx.copy(blueprint_value=union_starting_struct))}
