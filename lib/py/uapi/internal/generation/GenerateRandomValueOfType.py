from typing import List, Optional
import uapi
from uapi import RandomGenerator
from uapi.internal.types.UType import UType
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def generate_random_value_of_type(blueprint_value: object, use_blueprint_value: bool,
                                  include_optional_fields: bool, randomize_optional_fields: bool,
                                  generics: List['UTypeDeclaration'], random_generator: 'RandomGenerator',
                                  this_type: 'UType', nullable: bool,
                                  type_parameters: List['UTypeDeclaration']) -> Optional[object]:
    if nullable and not use_blueprint_value and random_generator.next_boolean():
        return None
    else:
        return this_type.generate_random_value(blueprint_value, use_blueprint_value, include_optional_fields,
                                               randomize_optional_fields, type_parameters, generics, random_generator)
