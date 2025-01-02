from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.RandomGenerator import RandomGenerator
    from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
    from uapi.internal.validation.ValidationFailure import ValidationFailure

from uapi.internal.types.UType import UType

_MOCK_STUB_NAME: str = "_ext.Stub_"


class UMockStub(UType):

    def __init__(self, types: dict[str, UType]) -> None:
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object, select: dict[str, object] | None, fn: str | None,
                 type_parameters: list['UTypeDeclaration']) -> list['ValidationFailure']:
        from uapi.internal.validation.ValidateMockStub import validate_mock_stub
        return validate_mock_stub(given_obj, select, fn, type_parameters, self.types)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: list['UTypeDeclaration'],
                              random_generator: 'RandomGenerator') -> object:
        raise NotImplementedError("Not implemented")

    def get_name(self) -> str:
        return _MOCK_STUB_NAME
