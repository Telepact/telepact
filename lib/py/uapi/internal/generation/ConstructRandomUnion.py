from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def construct_random_union(union_cases_reference: dict[str, 'UStruct'],
                           starting_union: dict[str, object],
                           include_optional_fields: bool,
                           randomize_optional_fields: bool,
                           random_generator: 'RandomGenerator') -> dict[str, object]:
    from uapi.internal.generation.ConstructRandomStruct import construct_random_struct

    if not starting_union:
        sorted_union_cases_reference = sorted(
            union_cases_reference.items(), key=lambda x: x[0])
        random_index = random_generator.next_int_with_ceiling(
            len(sorted_union_cases_reference) - 1)
        union_case, union_data = sorted_union_cases_reference[random_index]
        return {union_case: construct_random_struct(union_data.fields, {}, include_optional_fields,
                                                    randomize_optional_fields, random_generator)}
    else:
        union_case, union_starting_struct = cast(
            tuple[str, dict[str, object]], next(iter(starting_union.items())))
        union_struct_type = union_cases_reference[union_case]
        return {union_case: construct_random_struct(union_struct_type.fields, union_starting_struct,
                                                    include_optional_fields, randomize_optional_fields,
                                                    random_generator)}
