from typing import list, dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.types.UFieldDeclaration import UFieldDeclaration
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration

from uapi.internal.types.UType import UType

_STRUCT_NAME: str = "Object"


class UStruct(UType):

    def __init__(self, name: str, fields: dict[str, 'UFieldDeclaration'], type_parameter_count: int) -> None:
        self.name = name
        self.fields = fields
        self.type_parameter_count = type_parameter_count

    def get_type_parameter_count(self) -> int:
        return self.type_parameter_count

    def validate(self, value: object, select: dict[str, object], fn: str,
                 type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateStruct import validate_struct
        return validate_struct(value, select, fn, type_parameters, generics, self.name, self.fields)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration'],
                              random: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomStruct import generate_random_struct
        return generate_random_struct(blueprint_value, use_blueprint_value, include_optional_fields,
                                      randomize_optional_fields, type_parameters, generics, random, self.fields)

    def get_name(self, generics: list['UTypeDeclaration']) -> str:
        return _STRUCT_NAME
