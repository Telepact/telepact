from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UType, UTypeDeclaration
from uapi.internal.generation import GenerateRandomBoolean
from uapi.internal.validation import ValidateBoolean


class UBoolean(UType):
    _BOOLEAN_NAME: str = "Boolean"

    def getTypeParameterCount(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return ValidateBoolean.validateBoolean(value)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool,
                            includeOptionalFields: bool, randomizeOptionalFields: bool,
                            typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                            randomGenerator: RandomGenerator) -> object:
        return GenerateRandomBoolean.generateRandomBoolean(blueprintValue, useBlueprintValue, randomGenerator)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._BOOLEAN_NAME
