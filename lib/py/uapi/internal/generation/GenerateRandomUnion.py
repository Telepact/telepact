from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def generate_random_union(blueprint_value: object, use_blueprint_value: bool, include_optional_fields: bool,
                          randomize_optional_fields: bool, type_parameters: list['UTypeDeclaration'],
                          generics: list['UTypeDeclaration'], random_generator: 'RandomGenerator',
                          cases: dict[str, 'UStruct']) -> object:
    from uapi.internal.generation.ConstructRandomUnion import construct_random_union

    if use_blueprint_value:
        starting_union_case = cast(dict[str, object], blueprint_value)
        return construct_random_union(cases, starting_union_case, include_optional_fields,
                                      randomize_optional_fields, type_parameters, random_generator)
    else:
        return construct_random_union(cases, {}, include_optional_fields, randomize_optional_fields,
                                      type_parameters, random_generator)
