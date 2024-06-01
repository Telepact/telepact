from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


def construct_random_struct(reference_struct: Dict[str, 'UFieldDeclaration'],
                            starting_struct: Dict[str, Any],
                            include_optional_fields: bool,
                            randomize_optional_fields: bool,
                            type_parameters: List['UTypeDeclaration'],
                            random_generator: 'RandomGenerator') -> Dict[str, Any]:

    sorted_reference_struct = sorted(
        reference_struct.items(), key=lambda x: x[0])

    obj = {}
    for field_name, field_declaration in sorted_reference_struct:
        blueprint_value = starting_struct.get(field_name)
        use_blueprint_value = field_name in starting_struct
        type_declaration = field_declaration.type_declaration

        if use_blueprint_value:
            value = type_declaration.generate_random_value(blueprint_value, use_blueprint_value,
                                                           include_optional_fields, randomize_optional_fields,
                                                           type_parameters, random_generator)
        else:
            if not field_declaration.optional:
                value = type_declaration.generate_random_value(None, False,
                                                               include_optional_fields, randomize_optional_fields,
                                                               type_parameters, random_generator)
            else:
                if not include_optional_fields or (randomize_optional_fields and random_generator.next_boolean()):
                    continue
                value = type_declaration.generate_random_value(None, False,
                                                               include_optional_fields, randomize_optional_fields,
                                                               type_parameters, random_generator)

        obj[field_name] = value

    return obj
