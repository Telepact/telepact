from typing import List, Dict

from uapi.RandomGenerator import RandomGenerator
from uapi.internal.types.UType import UType
from uapi.internal.types.UTypeDeclaration import UTypeDeclaration
from uapi.internal.validation.ValidateMockCall import validate_mock_call
from uapi.internal.validation.ValidationFailure import ValidationFailure


class UMockCall(UType):
    _MOCK_CALL_NAME: str = "_ext.Call_"

    def __init__(self, types: Dict[str, UType]) -> None:
        self.types = types

    def get_type_parameter_count(self) -> int:
        return 0

    def validate(self, given_obj: object, select: Dict[str, object], fn: str,
                 type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return validate_mock_call(given_obj, select, fn, type_parameters, generics, self.types)

    def generate_random_value(self, blueprint_value: object, use_blueprint_value: bool,
                              include_optional_fields: bool, randomize_optional_fields: bool,
                              type_parameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                              random_generator: RandomGenerator) -> object:
        raise NotImplementedError("Not implemented")

    def get_name(self, generics: List[UTypeDeclaration]) -> str:
        return self._MOCK_CALL_NAME
