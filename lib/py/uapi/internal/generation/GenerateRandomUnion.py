from typing import List, Dict, Any
from uapi import RandomGenerator
from uapi.internal.types import UStruct, UTypeDeclaration
from uapi.internal.generation.ConstructRandomUnion import construct_random_union


def generate_random_union(blueprint_value: Any, use_blueprint_value: bool, include_optional_fields: bool,
                          randomize_optional_fields: bool, type_parameters: List[UTypeDeclaration],
                          generics: List[UTypeDeclaration], random_generator: RandomGenerator,
                          cases: Dict[str, UStruct]) -> Any:
    if use_blueprint_value:
        starting_union_case = blueprint_value
        return construct_random_union(cases, starting_union_case, include_optional_fields,
                                      randomize_optional_fields, type_parameters, random_generator)
    else:
        return construct_random_union(cases, {}, include_optional_fields, randomize_optional_fields,
                                      type_parameters, random_generator)
