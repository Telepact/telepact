from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ..validation.ValidationFailure import ValidationFailure
    from .VFieldDeclaration import VFieldDeclaration
    from .VTypeDeclaration import VTypeDeclaration
    from ..generation.GenerateContext import GenerateContext

from .VType import VType

_STRUCT_NAME: str = "Object"


class VStruct(VType):

    def __init__(self, name: str, fields: dict[str, 'VFieldDeclaration']) -> None:
        self.name = name
        self.fields = fields

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateStruct import validate_struct
        return validate_struct(value, self.name, self.fields, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomStruct import generate_random_struct
        return generate_random_struct(blueprint_value, use_blueprint_value, self.fields, ctx)

    def get_name(self) -> str:
        return _STRUCT_NAME
