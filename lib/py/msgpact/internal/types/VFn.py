from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .VTypeDeclaration import VTypeDeclaration
    from .VUnion import VUnion
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .VType import VType

_FN_NAME = "Object"


class VFn(VType):
    def __init__(self, name: str, call: 'VUnion', output: 'VUnion', errors_regex: str):
        self.name = name
        self.call = call
        self.result = output
        self.errors_regex = errors_regex

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, value: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        return self.call.validate(value, type_parameters, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomUnion import generate_random_union
        return generate_random_union(blueprint_value, use_blueprint_value, self.call.tags, ctx)

    def get_name(self) -> str:
        return _FN_NAME
