from typing import List, Any
from random import randint
from uapi.RandomGenerator import RandomGenerator
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def generate_random_array(blueprint_value: Any, use_blueprint_value: bool, include_optional_fields: bool,
                          randomize_optional_fields: bool, type_parameters: List['UTypeDeclaration'],
                          generics: List['UTypeDeclaration'], random_generator: 'RandomGenerator') -> List[Any]:
    nested_type_declaration = type_parameters[0]

    if use_blueprint_value:
        starting_array = blueprint_value

        array = []
        for starting_array_value in starting_array:
            value = nested_type_declaration.generate_random_value(starting_array_value, True,
                                                                  include_optional_fields,
                                                                  randomize_optional_fields, generics,
                                                                  random_generator)

            array.append(value)

        return array
    else:
        length = random_generator.next_collection_length()

        array = []
        for i in range(length):
            value = nested_type_declaration.generate_random_value(None, False, include_optional_fields,
                                                                  randomize_optional_fields, generics,
                                                                  random_generator)

            array.append(value)

        return array
