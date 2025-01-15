from typing import TYPE_CHECKING
from abc import ABCMeta, abstractmethod


if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext


class UType(metaclass=ABCMeta):
    @abstractmethod
    def get_type_parameter_count(self) -> int:
        pass

    @abstractmethod
    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        pass

    @abstractmethod
    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
