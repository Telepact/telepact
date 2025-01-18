from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.validation.ValidateContext import ValidateContext
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure
    from uapi.internal.generation.GenerateContext import GenerateContext

from uapi.internal.types.UType import UType


class UMockCall(UType):
    _MOCK_CALL_NAME: str = "_ext.Call_"

    def __init__(self, types: dict[str, UType]) -> None:
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object,
                 type_parameters: list['UTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateMockCall import validate_mock_call
        return validate_mock_call(given_obj, self.types, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['UTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from uapi.internal.generation.GenerateRandomUMockCall import generate_random_u_mock_call
        return generate_random_u_mock_call(self.types, ctx)

    def get_name(self) -> str:
        return self._MOCK_CALL_NAME
