from typing import List, Dict, Any
from abc import ABC, abstractmethod

from uapi.RandomGenerator import RandomGenerator
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
from uapi.internal.validation.ValidationFailure import ValidationFailure


class UType(ABC):
    @abstractmethod
    def get_type_parameter_count(self) -> int:
        pass

    @abstractmethod
    def validate(self, value: Any, select: Dict[str, Any], fn: str,
                 type_parameters: List[UTypeDeclaration],
                 generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        pass

    @abstractmethod
    def generate_random_value(self, blueprint_value: Any, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List[UTypeDeclaration],
                              generics: List[UTypeDeclaration],
                              random_generator: RandomGenerator) -> Any:
        pass

    @abstractmethod
    def get_name(self, generics: List[UTypeDeclaration]) -> str:
        pass
