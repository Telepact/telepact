from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext


class UType(metaclass=ABCMeta):
    @abstractmethod
    def get_type_parameter_count(self) -> int:
        pass

    @abstractmethod
    def validate(self, value: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        pass

    @abstractmethod
    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
