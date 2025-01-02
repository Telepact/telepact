from typing import TYPE_CHECKING
from uapi.internal.types.UType import UType

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UStruct import UStruct
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration

_UNION_NAME: str = "Object"


class UUnion(UType):

    def __init__(self, name: str, cases: dict[str, 'UStruct'], case_indices: dict[str, int]) -> None:
        self.name = name
        self.cases = cases
        self.case_indices = case_indices

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None, type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateUnion import validate_union
        return validate_union(value, select, fn, self.name, self.cases)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, include_optional_fields: bool, randomize_optional_fields: bool, type_parameters: list['UTypeDeclaration'], random: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomUnion import generate_random_union
        return generate_random_union(blueprint_value, use_blueprint_value, include_optional_fields, randomize_optional_fields, random, self.cases)

    def get_name(self) -> str:
        return _UNION_NAME
