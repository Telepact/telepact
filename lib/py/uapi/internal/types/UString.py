from typing import List, Dict
from uapi import RandomGenerator
from uapi.internal.validation import ValidationFailure
from uapi.internal.types import UType, UTypeDeclaration
from uapi.internal.generation import GenerateRandomString
from uapi.internal.validation import ValidateString


class UString(UType):
    _STRING_NAME: str = "String"

    def getTypeParameterCount(self) -> int:
        return 0

    def validate(self, value: object, select: Dict[str, object], fn: str,
                 typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration]) -> List[ValidationFailure]:
        return ValidateString.validateString(value)

    def generateRandomValue(self, blueprintValue: object, useBlueprintValue: bool,
                            includeOptionalFields: bool, randomizeOptionalFields: bool,
                            typeParameters: List[UTypeDeclaration], generics: List[UTypeDeclaration],
                            randomGenerator: RandomGenerator) -> object:
        return GenerateRandomString.generateRandomString(blueprintValue, useBlueprintValue, randomGenerator)

    def getName(self, generics: List[UTypeDeclaration]) -> str:
        return self._STRING_NAME
