from typing import List, Dict

from uapi.RandomGenerator import RandomGenerator
from uapi.internal.generation.GenerateRandomValueOfType import generate_random_value_of_type
from uapi.internal.types.UType import UType
from uapi.internal.validation.ValidateValueOfType import validate_value_of_type
from uapi.internal.validation.ValidationFailure import ValidationFailure


class UTypeDeclaration:
    def __init__(self, type: UType, nullable: bool, type_parameters: List['UTypeDeclaration']):
        self.type = type
        self.nullable = nullable
        self.type_parameters = type_parameters

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 generics: List['UTypeDeclaration']) -> List[ValidationFailure]:
        return validate_value_of_type(value, select, fn, generics, self.type, self.nullable, self.type_parameters)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              generics: List['UTypeDeclaration'], random_generator: RandomGenerator) -> object:
        return generate_random_value_of_type(blueprint_value, use_blueprint_value,
                                             include_optional_fields, randomize_optional_fields,
                                             generics, random_generator, self.type, self.nullable, self.type_parameters)
