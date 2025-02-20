from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...internal.validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from ...internal.validation.ValidationFailure import ValidationFailure
    from ...internal.types.UFieldDeclaration import UFieldDeclaration
    from ...internal.types.UTypeDeclaration import UTypeDeclaration
    from ...internal.generation.GenerateContext import GenerateContext

from ...internal.types.UType import UType

_STRUCT_NAME: str = "Object"


class UStruct(UType):

    def __init__(self, name: str, fields: dict[str, 'UFieldDeclaration']) -> None:
        self.name = name
        self.fields = fields

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ...internal.validation.ValidateStruct import validate_struct
        return validate_struct(value, self.name, self.fields, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ...internal.generation.GenerateRandomStruct import generate_random_struct
        return generate_random_struct(blueprint_value, use_blueprint_value, self.fields, ctx)

    def get_name(self) -> str:
        return _STRUCT_NAME
