from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure


from uapi.internal.types.UType import UType

_NUMBER_NAME: str = "Number"


class UNumber(UType):

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration']) -> List['ValidationFailure']:
        from uapi.internal.validation.ValidateNumber import validate_number
        return validate_number(value)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomNumber import generate_random_number
        return generate_random_number(blueprint_value, use_blueprint_value, random_generator)

    def get_name(self, generics: List['UTypeDeclaration']) -> str:
        return _NUMBER_NAME
