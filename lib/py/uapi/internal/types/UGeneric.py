from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure

from uapi.internal.types.UType import UType


class UGeneric(UType):
    def __init__(self, index: int):
        self.index = index

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration']) -> List['ValidationFailure']:
        type_declaration = generics[self.index]
        return type_declaration.validate(value, select, fn, [])

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        generic_type_declaration = generics[self.index]
        return generic_type_declaration.generate_random_value(blueprint_value, use_blueprint_value,
                                                              include_optional_fields, randomize_optional_fields,
                                                              [], random_generator)

    def get_name(self, generics: List['UTypeDeclaration']) -> str:
        type_declaration = generics[self.index]
        return type_declaration.type.get_name(generics)
