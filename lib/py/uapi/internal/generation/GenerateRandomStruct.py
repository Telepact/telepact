from typing import Any, Dict, List
from uapi import RandomGenerator
from uapi.internal.generation.ConstructRandomStruct import construct_random_struct
from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def generate_random_struct(blueprint_value: Any, use_blueprint_value: bool, include_optional_fields: bool,
                           randomize_optional_fields: bool, type_parameters: List['UTypeDeclaration'],
                           generics: List['UTypeDeclaration'], random_generator: 'RandomGenerator',
                           fields: Dict[str, 'UFieldDeclaration']) -> Any:
    if use_blueprint_value:
        # Assuming blueprint_value is already a dict
        starting_struct_value = blueprint_value
        return construct_random_struct(fields, starting_struct_value, include_optional_fields,
                                       randomize_optional_fields, type_parameters, random_generator)
    else:
        return construct_random_struct(fields, {}, include_optional_fields, randomize_optional_fields,
                                       type_parameters, random_generator)
