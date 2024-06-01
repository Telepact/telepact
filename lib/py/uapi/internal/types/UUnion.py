from typing import List, Dict, Any
from uapi.internal.generation.GenerateRandomUnion import generate_random_union
from uapi.internal.validation.ValidateUnion import validate_union
from uapi.RandomGenerator import RandomGenerator
from uapi.internal.validation.ValidationFailure import ValidationFailure
from uapi.internal.types.UType import UType
from uapi.internal.types.UStruct import UStruct
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration

_UNION_NAME: str = "Object"


class UUnion(UType):

    def __init__(self, name: str, cases: Dict[str, UStruct], case_indices: Dict[str, int], type_parameter_count: int) -> None:
        self.name = name
        self.cases = cases
        self.case_indices = case_indices
        self.type_parameter_count = type_parameter_count

    def get_type_parameter_count(self) -> int:
        return self.type_parameter_count

    def validate(self, value: Any, select: Dict[str, Any], fn: str, type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return validate_union(value, select, fn, type_parameters, generics, self.name, self.cases)

    def generate_random_value(self, blueprint_value: Any, use_blueprint_value: bool, include_optional_fields: bool, randomize_optional_fields: bool, type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration], random: RandomGenerator) -> Any:
        return generate_random_union(blueprint_value, use_blueprint_value, include_optional_fields, randomize_optional_fields, type_parameters, generics, random, self.cases)

    def get_name(self, generics: List[UTypeDeclaration]) -> str:
        return _UNION_NAME
