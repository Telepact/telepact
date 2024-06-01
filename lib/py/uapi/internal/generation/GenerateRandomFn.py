from typing import Any, Dict, List
from uapi import RandomGenerator
from uapi.internal.types import UStruct, UTypeDeclaration
from uapi.internal.generation.ConstructRandomUnion import construct_random_union


def generate_random_fn(blueprint_value: Any, use_blueprint_value: bool, include_optional_fields: bool,
                       randomize_optional_fields: bool, type_parameters: List[UTypeDeclaration],
                       generics: List[UTypeDeclaration], random_generator: RandomGenerator,
                       call_cases: Dict[str, UStruct]) -> Any:
    if use_blueprint_value:
        # Assuming blueprint_value is already a dictionary
        starting_fn_value = blueprint_value
        return construct_random_union(call_cases, starting_fn_value, include_optional_fields,
                                      randomize_optional_fields, [], random_generator)
    else:
        return construct_random_union(call_cases, {}, include_optional_fields, randomize_optional_fields,
                                      [], random_generator)
