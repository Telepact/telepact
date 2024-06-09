from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.validation.ValidationFailure import ValidationFailure

from uapi.internal.types.UType import UType

_FN_NAME = "Object"


class UFn(UType):
    def __init__(self, name: str, call: 'UUnion', output: 'UUnion', errors_regex: str):
        self.name = name
        self.call = call
        self.result = output
        self.errors_regex = errors_regex

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration']) -> List['ValidationFailure']:
        return self.call.validate(value, select, fn, type_parameters, generics)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List['UTypeDeclaration'], generics: List['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        from uapi.internal.generation.GenerateRandomFn import generate_random_fn
        return generate_random_fn(blueprint_value, use_blueprint_value, include_optional_fields,
                                  randomize_optional_fields, type_parameters, generics,
                                  random_generator, self.call.cases)

    def get_name(self, generics: List['UTypeDeclaration']) -> str:
        return _FN_NAME
