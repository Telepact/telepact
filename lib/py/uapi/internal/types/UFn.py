from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.types.UUnion import UUnion
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext

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

    def validate(self, value: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        return self.call.validate(value, select, fn, type_parameters)

    def generate_random_value(self, ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomUnion import generate_random_union
        return generate_random_union(self.call.cases, ctx)

    def get_name(self) -> str:
        return _FN_NAME
