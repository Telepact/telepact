from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType

_STRUCT_NAME: str = "Object"


class UStruct(UType):

    def __init__(self, name: str, fields: dict[str, 'UFieldDeclaration']) -> None:
        self.name = name
        self.fields = fields

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateStruct import validate_struct
        return validate_struct(value, self.name, self.fields, ctx)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomStruct import generate_random_struct
        return generate_random_struct(self.fields, ctx)

    def get_name(self) -> str:
        return _STRUCT_NAME
