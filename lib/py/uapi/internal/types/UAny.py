from typing import list, dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure

from uapi.internal.types.UType import UType


class Uobject(UType):
    _ANY_NAME = "object"

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: dict[str, object], fn: str,
                 type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration']) -> list['ValidationFailure']:
        return []

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: list['UTypeDeclaration'], generics: list['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomobject import generate_random_any
        return generate_random_any(random_generator)

    def get_name(self, generics: list['UTypeDeclaration']) -> str:
        return self._ANY_NAME
