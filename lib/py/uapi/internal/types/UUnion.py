from typing import TYPE_CHECKING
from uapi.internal.types.UType import UType

if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.internal.generation.GenerateContext import GenerateContext
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

    def validate(self, value: object, type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateUnion import validate_union
        return validate_union(value, self.name, self.cases, ctx)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomUnion import generate_random_union
        return generate_random_union(self.cases, ctx)

    def get_name(self) -> str:
        return _UNION_NAME
