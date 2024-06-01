from typing import List, Dict

from uapi.RandomGenerator import RandomGenerator
from uapi.internal.generation.GenerateRandomString import generate_random_string
from uapi.internal.types.UType import UType
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
from uapi.internal.validation.ValidateString import validate_string
from uapi.internal.validation.ValidationFailure import ValidationFailure

_STRING_NAME: str = "String"


class UString(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return validate_string(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                              random_generator: RandomGenerator) -> object:
        return generate_random_string(blueprint_value, use_blueprint_value, random_generator)

    def get_name(self, generics: List[UTypeDeclaration]) -> str:
        return _STRING_NAME
