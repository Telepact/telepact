from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi import RandomGenerator
    from uapi.internal.types.UType import UType
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration


from uapi.internal.validation.ValidationFailure import ValidationFailure


class UAny(UType):
    _ANY_NAME = "Any"

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration']) -> List['ValidationFailure']:
        return []

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomAny import generate_random_any
        return generate_random_any(random_generator)

    def get_name(self, generics: List['UTypeDeclaration']) -> str:
        return self._ANY_NAME
