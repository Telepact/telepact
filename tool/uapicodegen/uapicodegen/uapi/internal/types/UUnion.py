from typing import TYPE_CHECKING
from ...internal.types.UType import UType

if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...internal.generation.GenerateContext import GenerateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.types.UStruct import UStruct
    from ...internal.types.UTypeDeclaration import UTypeDeclaration

_UNION_NAME: str = "Object"


class UUnion(UType):

    def __init__(self, name: str, tags: dict[str, 'UStruct'], tag_indices: dict[str, int]) -> None:
        self.name = name
        self.tags = tags
        self.tag_indices = tag_indices

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateUnion import validate_union
        return validate_union(value, self.name, self.tags, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomUnion import generate_random_union
        return generate_random_union(blueprint_value, use_blueprint_value, self.tags, ctx)

    def get_name(self) -> str:
        return _UNION_NAME
