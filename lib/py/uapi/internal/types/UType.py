from typing import list, dict, object, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure


class UType(ABC):
    @abstractmethod
    def get_type_parameter_count(self) -> int:
        pass

    @abstractmethod
    def validate(self, value: object, select: dict[str, object], fn: str,
                 type_parameters: list['UTypeDeclaration'],
                 generics: list['UTypeDeclaration']) -> list['ValidationFailure']:
        pass

    @abstractmethod
    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: list['UTypeDeclaration'],
                              generics: list['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        pass

    @abstractmethod
    def get_name(self, generics: list['UTypeDeclaration']) -> str:
        pass
