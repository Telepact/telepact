from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..validation.ValidateContext import ValidateContext
    from ...RandomGenerator import RandomGenerator
    from .VTypeDeclaration import VTypeDeclaration
    from ..validation.ValidationFailure import ValidationFailure
    from ..generation.GenerateContext import GenerateContext

from .VType import VType

_MOCK_STUB_NAME: str = "_ext.Stub_"


class VMockStub(VType):

    def __init__(self, types: dict[str, VType]) -> None:
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object,
                 type_parameters: list['VTypeDeclaration'], ctx: 'ValidateContext') -> list['ValidationFailure']:
        from ..validation.ValidateMockStub import validate_mock_stub
        return validate_mock_stub(given_obj, self.types, ctx)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool, type_parameters: list['VTypeDeclaration'], ctx: 'GenerateContext') -> object:
        from ..generation.GenerateRandomUMockStub import generate_random_u_mock_stub
        return generate_random_u_mock_stub(self.types, ctx)

    def get_name(self) -> str:
        return _MOCK_STUB_NAME
